import logging
import json
from typing import Dict, Any, AsyncGenerator

from app.orchestrator.ai_session import AISession
from app.orchestrator.gateway import ConversationGateway
from app.orchestrator.llm_provider import StreamingLLMProvider
from app.orchestrator.router import router as intent_router
from app.orchestrator.state_adapter import state_adapter

from app.red_flag_detector import RedFlagDetector
from app.models.red_flag import RedFlagSeverity
from app.interview.adaptive_engine import AdaptiveInterviewEngine
from app.interview.question_bank import QuestionBank
from app.interview.evidence_collector import EvidenceCollector
from app.severity_classifier import SeverityClassifier
from app.config import settings

logger = logging.getLogger(__name__)

AURA_SYSTEM_PROMPT = (
    "You are AURA, an AI-powered Clinical Decision Support assistant. "
    "You help patients think through symptoms, understand triage recommendations, and decide on next steps. "
    "Always recommend consulting a qualified healthcare professional for diagnosis and treatment. "
    "Be compassionate, clear, and medically responsible. "
    "Never diagnose. Never prescribe. Never contradict a triage level you have been given.\n\n"
)


class AIOrchestrator:
    def __init__(self):
        self.gateway = ConversationGateway()
        self.red_flag_detector = RedFlagDetector()
        self.adaptive_engine = AdaptiveInterviewEngine()
        self.severity_classifier = SeverityClassifier()
        self.question_bank = QuestionBank()
        self.evidence_collector = EvidenceCollector()
        # Use provider configured in .env (gemini by default)
        self.llm_provider = StreamingLLMProvider(settings.LLM_PROVIDER)

    async def _extract_clinical_entities(self, text: str) -> dict:
        """
        Extract clinical entities from patient text using fast heuristics + LLM fallback.
        Returns dict: {chief_complaint, symptoms, duration, severity}
        """
        common_symptoms = [
            "chest pain", "shortness of breath", "difficulty breathing",
            "headache", "fever", "cough", "nausea", "vomiting", "dizziness",
            "sore throat", "stomach pain", "abdominal pain", "back pain",
            "fatigue", "rash", "weakness", "numbness", "chills", "diarrhea"
        ]
        text_lower = text.lower()
        matched = [s for s in common_symptoms if s in text_lower]
        if matched:
            return {
                "chief_complaint": matched[0],
                "symptoms": matched,
                "duration": "",
                "severity": None
            }

        try:
            prompt = (
                "Extract clinical information from this patient message as JSON only. "
                "Return a JSON object with these keys: "
                "chief_complaint (string), symptoms (array of strings), "
                "duration (string, empty if not mentioned), severity (integer 1-10 or null). "
                "Output ONLY valid JSON — no markdown, no explanation.\n\n"
                f"Patient message: {text}"
            )
            raw = ""
            async for chunk in self.llm_provider._stream_openrouter(prompt, model="nvidia/nemotron-3.5-lightning:free"):
                raw += chunk
                if len(raw) > 300:
                    break

            # Strip markdown fences if present
            cleaned = raw.strip()
            if "```" in cleaned:
                parts = cleaned.split("```")
                if len(parts) >= 2:
                    cleaned = parts[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
            cleaned = cleaned.strip()

            data = json.loads(cleaned)
            return data
        except Exception as e:
            logger.debug("Clinical entity extraction fallback: %s", e)
            return {"chief_complaint": text, "symptoms": [], "duration": "", "severity": None}

    async def handle_message_async_stream(
        self,
        user_id: str,
        conversation_id: str,
        payload: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:

        session = self.gateway.handle_request(user_id, conversation_id, payload)
        user_message = payload.get("msg", "").strip()
        fallback_reply = (
            "Hello — I'm AURA. I can help you think through symptoms, medications, "
            "or next steps. What would you like to share?"
        )

        try:
            full_response = ""

            pending_q_id = session.context_data.get("pending_question_id")
            if pending_q_id:
                # User is answering an active interview question
                intent = "clinical_intake"
                extracted_facts = {"chief_complaint": "", "symptoms": [], "duration": "", "severity": None}
            else:
                yield {"event": "PROGRESS", "data": json.dumps({"message": "Analyzing your message..."})}
                extracted_facts = await self._extract_clinical_entities(user_message)
                symptoms = extracted_facts.get("symptoms", [])
                chief_complaint = extracted_facts.get("chief_complaint", "").strip()
                has_clinical_content = bool(symptoms) or bool(chief_complaint)
                intent = "clinical_intake" if has_clinical_content else intent_router.route(user_message)

            if intent == "clinical_intake":
                yield {"event": "PROGRESS", "data": json.dumps({"message": "Processing clinical context..."})}

                session_state = state_adapter.to_session_state(session)
                clinical_input = state_adapter.to_clinical_input(session)
                interview_state = state_adapter.to_interview_state(session)

                pending_q_id = session.context_data.get("pending_question_id")

                if pending_q_id:
                    # User is answering a pending interview question
                    last_question = self.question_bank.get_question_by_id(pending_q_id)
                    if last_question:
                        self.evidence_collector.process_interview_answer(last_question, user_message, interview_state)
                        clinical_input = self.evidence_collector.build_updated_clinical_input(clinical_input, interview_state)
                        session_state.symptoms = clinical_input.symptoms.copy()
                        session_state.symptom_duration = clinical_input.symptom_duration
                        session_state.symptom_severity = clinical_input.symptom_severity
                    session.context_data["pending_question_id"] = None
                else:
                    # First turn — establish chief complaint and initial symptoms
                    from app.interview.models import EvidenceSource
                    cc = chief_complaint or user_message
                    session_state.chief_complaint = cc
                    clinical_input.chief_complaint = cc

                    for sym in symptoms:
                        self.evidence_collector.ingest_external_evidence(
                            source=EvidenceSource.NLU,
                            key="symptom",
                            value=sym,
                            symptom_tags=[sym.lower()],
                            state=interview_state
                        )

                    sev_val = extracted_facts.get("severity")
                    if sev_val is not None:
                        clinical_input.symptom_severity = sev_val
                    dur_val = extracted_facts.get("duration")
                    if dur_val:
                        clinical_input.symptom_duration = dur_val

                    clinical_input = self.evidence_collector.build_updated_clinical_input(clinical_input, interview_state)
                    session_state.symptoms = clinical_input.symptoms.copy()

                # --- DETERMINISTIC GATE 1: Red Flag Detection ---
                rf_result = self.red_flag_detector.evaluate(session_state)

                if rf_result.highest_severity == RedFlagSeverity.EMERGENCY:
                    yield {"event": "PROGRESS", "data": json.dumps({"message": "High-risk pattern detected..."})}

                    explanations = [
                        f.explanation for f in rf_result.flags_matched
                        if f.severity == RedFlagSeverity.EMERGENCY
                    ]
                    emergency_reason = " ".join(explanations) if explanations else "Emergency symptoms detected."

                    # Deterministic safety response — Gemini is NOT called here
                    deterministic_response = (
                        "⚠️ **EMERGENCY DETECTED**\n\n"
                        f"**Reason:** {emergency_reason}\n\n"
                        "Your reported symptoms may require **immediate medical attention**. "
                        "Please call emergency services (911 / 112) or go to the nearest emergency room immediately.\n\n"
                        "*This is a deterministic safety alert — not an AI-generated opinion.*"
                    )

                    full_response = deterministic_response
                    yield {"event": "TEXT_CHUNK", "data": json.dumps({"text": deterministic_response})}
                    session.transition_state("COMPLETED")
                    yield {"event": "COMPLETE", "data": json.dumps({"status": "done", "full_response": full_response})}
                    return

                # --- GATE 2: Adaptive Interview ---
                selection_result = self.adaptive_engine.evaluate_and_select_next(clinical_input, interview_state)
                reasoning_output = selection_result.current_reasoning_output

                if not selection_result.is_complete and selection_result.selected_question:
                    next_q = selection_result.selected_question.text
                    session.context_data["pending_question_id"] = selection_result.selected_question.question_id

                    state_adapter.save_session_state(session, session_state)
                    state_adapter.save_clinical_input(session, clinical_input)
                    state_adapter.save_interview_state(session, interview_state)

                    full_response = next_q
                    yield {"event": "TEXT_CHUNK", "data": json.dumps({"text": next_q})}
                    session.transition_state("WAITING_FOR_USER")
                    yield {"event": "COMPLETE", "data": json.dumps({"status": "done", "full_response": full_response})}
                    return

                # --- DETERMINISTIC GATE 3: Severity Classification ---
                triage_decision = self.severity_classifier.classify(session_state, rf_result)

                session.context_data["pending_question_id"] = None
                state_adapter.save_session_state(session, session_state)
                state_adapter.save_clinical_input(session, clinical_input)
                state_adapter.save_interview_state(session, interview_state)

                candidate_str = "\n".join(
                    f"- {c.name} (confidence: {c.confidence:.0%})"
                    for c in reasoning_output.possible_conditions[:3]
                ) or "None identified"

                rf_str = "\n".join(
                    f"- {rf.factor_name}"
                    for rf in reasoning_output.risk_factors
                ) or "None"

                # Gemini explains the DETERMINISTIC result — it cannot change it
                structured_prompt = (
                    AURA_SYSTEM_PROMPT
                    + f"Patient message: {user_message}\n\n"
                    "--- CLINICAL ASSESSMENT (Deterministic — do not override) ---\n"
                    f"Severity: {triage_decision.triage_level.value}\n"
                    f"Risk factors identified:\n{rf_str}\n"
                    f"Possible conditions for context:\n{candidate_str}\n"
                    "---\n\n"
                    "Explain this assessment to the patient in clear, empathetic language. "
                    "State the severity level clearly. Provide appropriate next-step guidance. "
                    "Do NOT diagnose. Do NOT prescribe. Do NOT lower the severity."
                )

                yield {"event": "PROGRESS", "data": json.dumps({"message": "Generating clinical response..."})}

                try:
                    async for text_chunk in self.llm_provider.generate_stream(structured_prompt):
                        full_response += text_chunk
                        yield {"event": "TEXT_CHUNK", "data": json.dumps({"text": text_chunk})}
                except Exception as llm_err:
                    logger.error("LLM stream failed in clinical path: %s", llm_err, exc_info=True)
                    # Safe fallback that still communicates the deterministic result
                    fallback_text = (
                        f"Based on your symptoms, the assessment indicates a **{triage_decision.triage_level.value}** situation. "
                        "Please follow appropriate guidance for this level and consult a healthcare professional."
                    )
                    full_response = fallback_text
                    yield {"event": "TEXT_CHUNK", "data": json.dumps({"text": fallback_text})}

            else:
                # General health conversation (greetings, general questions, etc.)
                yield {"event": "PROGRESS", "data": json.dumps({"message": "Generating response..."})}

                direct_prompt = AURA_SYSTEM_PROMPT + f"User: {user_message}\n\nAURA:"

                try:
                    async for text_chunk in self.llm_provider.generate_stream(direct_prompt):
                        full_response += text_chunk
                        yield {"event": "TEXT_CHUNK", "data": json.dumps({"text": text_chunk})}
                except Exception as llm_err:
                    logger.error("LLM stream failed in general path: %s", llm_err, exc_info=True)

            if not full_response.strip():
                full_response = fallback_reply
                yield {"event": "TEXT_CHUNK", "data": json.dumps({"text": full_response})}

            session.transition_state("COMPLETED")
            yield {"event": "COMPLETE", "data": json.dumps({"status": "done", "full_response": full_response})}

        except Exception as e:
            logger.error("Orchestrator execution failed: %s", e, exc_info=True)
            session.transition_state("ERROR")
            yield {
                "event": "ERROR",
                "data": json.dumps({
                    "message": "I hit a problem generating that reply. Please try again, or describe your symptoms in more detail."
                })
            }


orchestrator_service = AIOrchestrator()
