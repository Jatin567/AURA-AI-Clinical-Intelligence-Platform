import uuid
from fastapi import APIRouter, Depends, Header, HTTPException, status, Request
from redis.asyncio import Redis
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.triage import TriageLevel
from app.models.session import SessionState
from app.api.schemas import (
    AnswerRequest, 
    SessionCreatedResponse, 
    QuestionResponse, 
    AnswerResponse
)
from app.dependencies import get_redis_client, get_current_session
from app.session_manager import create_session, update_session
from app.intake_engine import IntakeEngine, IntakeValidationError, IntakeAlreadyCompleteError
from app.red_flag_detector import RedFlagDetector
from app.severity_classifier import SeverityClassifier
from app.llm_orchestrator import LLMOrchestrator
from app.otc_suggester import OTCSuggester
from app.triage_output_builder import TriageOutputBuilder
from app.db.database import get_db_session
from app.db.models import TriageSession
from app.audit_logger import (
    log_red_flag_evaluation,
    log_triage_classification,
    log_otc_evaluation,
    log_output_assembled,
    log_session_error
)

VALID_REGIONS = frozenset([
    "US", "CA", "GB", "AU", "DE", "FR", "ES", "IT", "JP", 
    "BR", "MX", "IN", "CN", "RU", "ZA", "NG", "EG", "KE"
])

def get_user_region(request: Request) -> str:
    header = request.headers.get("X-User-Region", "US").upper()
    return header if header in VALID_REGIONS else "US"

router = APIRouter(tags=["session"])

from app.reasoning import ClinicalReasoningEngine, ClinicalInput

# Initialize engine components
intake_engine = IntakeEngine()
red_flag_detector = RedFlagDetector()
severity_classifier = SeverityClassifier()
llm_orchestrator = LLMOrchestrator()
otc_suggester = OTCSuggester()
triage_output_builder = TriageOutputBuilder()
clinical_reasoning_engine = ClinicalReasoningEngine()

@router.post("/session", response_model=SessionCreatedResponse)
async def post_session(redis: Redis = Depends(get_redis_client)):
    """Creates a new triage session."""
    session = await create_session(redis)
    return SessionCreatedResponse(
        session_id=session.session_id,
        expires_at=session.expires_at
    )

@router.get("/session/question", response_model=QuestionResponse)
async def get_question(session: SessionState = Depends(get_current_session)):
    """Returns the next intake question."""
    try:
        question = intake_engine.get_next_question(session)
        return QuestionResponse(
            question_id=question.question_id,
            text=question.text,
            input_type=question.input_type,
            options=question.options,
            intake_complete=False
        )
    except IntakeAlreadyCompleteError:
        return QuestionResponse(
            question_id="",
            text="",
            input_type="",
            intake_complete=True
        )

@router.post("/session/answer", response_model=AnswerResponse)
async def post_answer(
    request: Request,
    answer_request: AnswerRequest,
    session: SessionState = Depends(get_current_session),
    redis: Redis = Depends(get_redis_client),
    db: AsyncSession = Depends(get_db_session)
):
    """Processes a user answer and triggers triage if intake is complete."""
    try:
        user_region = get_user_region(request)
        # 1. Process Answer
        intake_engine.process_answer(session, answer_request.answer, answer_request.question_id)
        
        # 2. Update session with answer
        await update_session(redis, session.session_id, session.model_dump(exclude={"session_id"}))
        
        intake_complete = intake_engine.is_intake_complete(session)
        
        # 3. Trigger Pipeline if complete
        if intake_complete:
            try:
                # Gate 1: Red Flags
                red_flag_result = red_flag_detector.evaluate(session)
                try:
                    await log_red_flag_evaluation(session.session_id, red_flag_result)
                except Exception: pass
                
                # Gate 2: Severity Classifer
                triage_decision = severity_classifier.classify(session, red_flag_result)
                try:
                    await log_triage_classification(session.session_id, triage_decision, db)
                except Exception: pass
                
                # Gate 3: LLM Orchestration
                orchestrator_result = await llm_orchestrator.generate_explanation(session, triage_decision)
                
                # Gate 4: OTC Suggestions
                candidates = orchestrator_result.llm_response.otc_candidates if orchestrator_result.llm_response else []
                otc_result = otc_suggester.validate(session, candidates, triage_decision.triage_level)
                try:
                    await log_otc_evaluation(session.session_id, otc_result, db)
                except Exception: pass
                
                # Gate 5: Final Assembly & Clinical Reasoning Evaluation
                triage_output = triage_output_builder.build(
                    session, orchestrator_result, otc_result, user_region=user_region
                )
                
                # Evaluate Clinical Reasoning Engine for internal intelligence audit
                clinical_input_obj = ClinicalInput(
                    symptoms=session.symptoms,
                    chief_complaint=session.chief_complaint,
                    symptom_duration=session.symptom_duration,
                    symptom_severity=session.symptom_severity,
                    age=session.patient_profile.age if session.patient_profile else None,
                    sex=session.patient_profile.sex if session.patient_profile else None,
                    chronic_conditions=session.patient_profile.known_conditions if session.patient_profile else [],
                    medications=getattr(session.patient_profile, "current_medications", []),
                    allergies=getattr(session.patient_profile, "allergies", [])
                )
                reasoning_eval = clinical_reasoning_engine.evaluate(clinical_input_obj)

                result_dict = triage_output.model_dump()
                result_dict["clinical_reasoning"] = reasoning_eval.model_dump()

                try:
                    await log_output_assembled(session.session_id, triage_output, db)
                except Exception: pass
                
                # Save Result to Session (Redis)
                await update_session(redis, session.session_id, {"triage_result": result_dict})

                # MIRROR to SQL for Reporting (Denormalized Flags)
                try:
                    sess_uuid = uuid.UUID(session.session_id)
                    db_session_row = await db.get(TriageSession, sess_uuid)
                    if not db_session_row:
                        db_session_row = TriageSession(
                            id=sess_uuid,
                            created_at=session.created_at,
                            expires_at=session.expires_at,
                            intake_stage=session.intake_stage.value
                        )
                        db.add(db_session_row)
                    
                    db_session_row.triage_level = triage_decision.triage_level.value
                    db_session_row.triage_label = triage_decision.triage_label
                    db_session_row.completed_at = datetime.now(timezone.utc)
                    db_session_row.had_emergency = (triage_decision.triage_level == TriageLevel.EMERGENCY)
                    db_session_row.had_crisis_flag = any(
                        getattr(m, "requires_immediate_crisis_resource", False) 
                        for m in red_flag_result.flags_matched
                    )
                    await db.flush() # Commit is handled by dependency lifespan
                except Exception as db_err:
                    import sys
                    sys.stderr.write(f"DATABASE MIRROR FAILURE for session {session.session_id}: {str(db_err)}\n")
            except Exception as e:
                import sys
                # Pipeline failure must not return 500
                sys.stderr.write(f"TRIAGE PIPELINE FAILURE for session {session.session_id}: {str(e)}\n")
                
                # Audit the error
                try:
                    await log_session_error(session.session_id, type(e).__name__, str(e), db)
                except Exception: pass

                await update_session(redis, session.session_id, {
                    "triage_result": {
                        "error": "Triage pipeline failed. Please try again or seek medical attention if urgent."
                    }
                })
        
        return AnswerResponse(
            answered=True,
            intake_complete=intake_complete
        )

    except IntakeValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@router.get("/session/result")
async def get_result(request: Request, session: SessionState = Depends(get_current_session)):
    """Returns the full triage result if complete."""
    _ = get_user_region(request) # Ensure validation even if not re-building
    if not session.triage_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Triage not yet complete"
        )
    
    if "error" in session.triage_result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=session.triage_result["error"]
        )
        
    return session.triage_result
