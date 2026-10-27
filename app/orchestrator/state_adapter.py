from datetime import datetime, timezone
from app.orchestrator.ai_session import AISession
from app.models.session import SessionState, IntakeStage, PatientProfile
from app.reasoning.models import ClinicalInput
from app.interview.models import InterviewState, ClinicalEvidence

class StateAdapter:
    """
    Deterministically projects the canonical AISession into the specific objects
    required by the legacy clinical engines, ensuring state never silently diverges.
    """
    
    @staticmethod
    def to_session_state(session: AISession) -> SessionState:
        data = session.context_data.get("session_state", {})
        
        # Populate defaults if empty
        return SessionState(
            session_id=session.session_id,
            created_at=data.get("created_at", datetime.now(timezone.utc)),
            expires_at=data.get("expires_at", datetime.now(timezone.utc)), # Stub
            intake_stage=IntakeStage(data.get("intake_stage", "demographics")),
            patient_profile=PatientProfile(**data.get("patient_profile", {})),
            chief_complaint=data.get("chief_complaint"),
            symptom_duration=data.get("symptom_duration"),
            symptom_severity=data.get("symptom_severity"),
            symptoms=data.get("symptoms", []),
            red_flags_detected=data.get("red_flags_detected", []),
            triage_result=data.get("triage_result"),
            conversation_history=data.get("conversation_history", [])
        )

    @staticmethod
    def save_session_state(session: AISession, state: SessionState):
        session.context_data["session_state"] = state.model_dump(mode="json")

    @staticmethod
    def to_clinical_input(session: AISession) -> ClinicalInput:
        data = session.context_data.get("clinical_input", {})
        
        # We also sync basic info from session_state if available
        sess_data = session.context_data.get("session_state", {})
        profile = sess_data.get("patient_profile", {})
        
        return ClinicalInput(
            symptoms=sess_data.get("symptoms", data.get("symptoms", [])),
            chief_complaint=sess_data.get("chief_complaint", data.get("chief_complaint")),
            symptom_duration=sess_data.get("symptom_duration", data.get("symptom_duration")),
            symptom_severity=sess_data.get("symptom_severity", data.get("symptom_severity")),
            age=profile.get("age", data.get("age")),
            sex=profile.get("sex", data.get("sex")),
            chronic_conditions=profile.get("known_conditions", data.get("chronic_conditions", [])),
            medications=profile.get("current_medications", data.get("medications", [])),
            allergies=profile.get("allergies", data.get("allergies", []))
        )

    @staticmethod
    def save_clinical_input(session: AISession, input_obj: ClinicalInput):
        session.context_data["clinical_input"] = input_obj.model_dump(mode="json")

    @staticmethod
    def to_interview_state(session: AISession) -> InterviewState:
        data = session.context_data.get("interview_state", {})
        raw_evidence = data.get("gathered_evidence", [])
        gathered_evidence = [ClinicalEvidence(**e) for e in raw_evidence]
        
        return InterviewState(
            session_id=session.session_id,
            gathered_evidence=gathered_evidence,
            turn_count=data.get("turn_count", 0),
            asked_question_ids=data.get("asked_question_ids", []),
            is_complete=data.get("is_complete", False),
            completion_reason=data.get("completion_reason")
        )

    @staticmethod
    def save_interview_state(session: AISession, state: InterviewState):
        session.context_data["interview_state"] = state.model_dump(mode="json")

state_adapter = StateAdapter()
