from typing import Optional, List, Any
from datetime import datetime, timezone
from app.models.session import SessionState, IntakeStage, PatientProfile
from app.models.intake import IntakeQuestion


class IntakeValidationError(Exception):
    """Raised when an answer fails validation."""
    pass


class IntakeAlreadyCompleteError(Exception):
    """Raised when get_next_question is called but intake is already complete."""
    pass


QUESTION_TREE = {
    IntakeStage.DEMOGRAPHICS: [
        IntakeQuestion(
            question_id="age",
            text="What is your age?",
            field_target="patient_profile.age",
            input_type="number",
            required=True
        ),
        IntakeQuestion(
            question_id="age_in_days",
            text="How many days old is the infant? (0-365)",
            field_target="patient_profile.age_in_days",
            input_type="number",
            required=True
        ),
        IntakeQuestion(
            question_id="is_infant_under_3_months",
            text="Is the child under 3 months old?",
            field_target="patient_profile.is_infant",
            input_type="yes_no",
            required=True
        ),
        IntakeQuestion(
            question_id="sex",
            text="What is your sex?",
            field_target="patient_profile.sex",
            input_type="text",
            options=["male", "female", "other"],
            required=True
        ),
        IntakeQuestion(
            question_id="known_conditions",
            text="Do you have any known medical conditions?",
            field_target="patient_profile.known_conditions",
            input_type="multi_select",
            options=["diabetes", "hypertension", "asthma", "none"],
            required=False
        ),
        IntakeQuestion(
            question_id="current_medications",
            text="Are you currently taking any medications?",
            field_target="patient_profile.current_medications",
            input_type="multi_select",
            required=False
        ),
        IntakeQuestion(
            question_id="allergies",
            text="Do you have any allergies?",
            field_target="patient_profile.allergies",
            input_type="multi_select",
            required=False
        ),
    ],
    IntakeStage.SYMPTOMS: [
        IntakeQuestion(
            question_id="chief_complaint",
            text="What is your chief complaint? (Why are you seeking medical attention?)",
            field_target="chief_complaint",
            input_type="text",
            required=True
        ),
        IntakeQuestion(
            question_id="symptom_duration",
            text="How long have you had this symptom?",
            field_target="symptom_duration",
            input_type="text",
            required=True
        ),
        IntakeQuestion(
            question_id="symptom_severity",
            text="On a scale of 1-10, how severe is the symptom?",
            field_target="symptom_severity",
            input_type="number",
            required=True
        ),
        IntakeQuestion(
            question_id="associated_symptoms",
            text="Are you experiencing any associated symptoms?",
            field_target="symptoms",
            input_type="multi_select",
            options=["fever", "nausea", "dizziness", "fatigue", "none"],
            required=False
        ),
    ],
    IntakeStage.HISTORY: [
        IntakeQuestion(
            question_id="better",
            text="Does anything make the symptom better?",
            field_target="conversation_history",
            input_type="text",
            required=False
        ),
        IntakeQuestion(
            question_id="worse",
            text="Does anything make the symptom worse?",
            field_target="conversation_history",
            input_type="text",
            required=False
        ),
        IntakeQuestion(
            question_id="previous_occurrence",
            text="Have you had this symptom before?",
            field_target="conversation_history",
            input_type="yes_no",
            required=False
        ),
    ]
}


class IntakeEngine:
    """
    Handles the medical intake flow by serving deterministic questions 
    and processing user answers.
    """

    def get_next_question(self, session: SessionState) -> Optional[IntakeQuestion]:
        """
        Returns the next unanswered question based on current stage and session state.
        """
        if session.intake_stage == IntakeStage.COMPLETE:
            raise IntakeAlreadyCompleteError("Cannot get next question: intake is already complete.")

        # Check questions in the current stage
        questions = QUESTION_TREE.get(session.intake_stage, [])
        for q in questions:
            # Conditional logic for infant questions
            if q.question_id == "is_infant_under_3_months":
                age = session.patient_profile.age if session.patient_profile else None
                if age is not None and age != 0: # Only ask if age is 0
                    continue
            
            if q.question_id == "age_in_days":
                age = session.patient_profile.age if session.patient_profile else None
                if age is not None and age != 0: # Only ask if age is 0
                    continue

            if not self._is_answered(session, q):
                return q

        # If all in current stage answered, try to advance stage and re-call
        next_stage_map = {
            IntakeStage.DEMOGRAPHICS: IntakeStage.SYMPTOMS,
            IntakeStage.SYMPTOMS: IntakeStage.HISTORY,
            IntakeStage.HISTORY: IntakeStage.COMPLETE
        }
        
        next_stage = next_stage_map.get(session.intake_stage)
        if next_stage and next_stage != IntakeStage.COMPLETE:
            # Peek into next stage
            next_questions = QUESTION_TREE.get(next_stage, [])
            for question in next_questions:
                if not self._is_answered(session, question):
                    return question
        
        return None

    def process_answer(self, session: SessionState, answer: Any, question_id: Optional[str] = None) -> SessionState:
        """
        Parses the answer, updates the session, and advances the stage if necessary.
        """
        if question_id:
            question = self._find_question_by_id(question_id)
        else:
            question = self.get_next_question(session)

        if not question:
            return session

        # 1. Validation
        validated_value = self._validate_answer(question, answer)

        # 2. Update session field
        self._set_session_field(session, question.field_target, validated_value)
        
        # GAP 1: Reset age_in_days if age > 0
        if question.question_id == "age" and validated_value > 0:
            session.patient_profile.age_in_days = None
        
        # 3. Add to or update conversation history
        now_ts = datetime.now(timezone.utc).isoformat()
        history_entry = {
            "question_id": question.question_id,
            "question_text": question.text,
            "answer": str(validated_value),
            "timestamp": now_ts
        }
        
        # Check if question already in history (correction)
        existing_index = next((i for i, entry in enumerate(session.conversation_history) 
                              if entry["question_id"] == question.question_id), None)
        
        if existing_index is not None:
            session.conversation_history[existing_index] = history_entry
        else:
            session.conversation_history.append(history_entry)
            
        if len(session.conversation_history) > 100:
            session.conversation_history = session.conversation_history[-100:]

        # 4. Advance Stage if needed
        self._check_and_advance_stage(session)

        return session

    def is_intake_complete(self, session: SessionState) -> bool:
        """
        Returns True when intake_stage == complete and minimum required fields are populated.
        """
        if session.intake_stage != IntakeStage.COMPLETE:
            return False
        
        if session.patient_profile.age is None:
            return False
        if not session.chief_complaint:
            return False
            
        return True

    def _is_answered(self, session: SessionState, question: IntakeQuestion) -> bool:
        """Checks if a specific question has been answered in the session."""
        # Special case for infant questions: if age is not 0, they're considered "answered" (skipped)
        if question.question_id in ["is_infant_under_3_months", "age_in_days"]:
            age = session.patient_profile.age if session.patient_profile else None
            if age is not None and age != 0:
                return True

        val = self._get_session_field(session, question.field_target)
        
        if question.field_target == "symptoms" or question.field_target == "conversation_history":
            return any(entry.get("question_id") == question.question_id for entry in session.conversation_history)

        if val is None:
            return False
        if isinstance(val, (list, dict)) and not val:
            return False
        return True

    def _get_session_field(self, session: SessionState, target: str) -> Any:
        """Gets nested session field using dot notation."""
        parts = target.split(".")
        obj = session
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return None
        return obj

    def _set_session_field(self, session: SessionState, target: str, value: Any) -> None:
        """Sets nested session field using dot notation."""
        if target == "conversation_history":
            # Already handled by process_answer's history append
            return

        parts = target.split(".")
        if len(parts) == 1:
            setattr(session, target, value)
            return

        obj = session
        for part in parts[:-1]:
            obj = getattr(obj, part)
        
        setattr(obj, parts[-1], value)

    def _validate_answer(self, question: IntakeQuestion, answer: Any) -> Any:
        """Validates answer against input type and constraints."""
        if isinstance(answer, str) and len(answer) > 1000:
            raise IntakeValidationError("Answer exceeds maximum length of 1000 characters.")

        if question.input_type == "number":
            try:
                val = int(answer)
                if question.question_id == "age" and not (0 <= val <= 120):
                    raise IntakeValidationError("Age must be between 0 and 120.")
                if question.question_id == "age_in_days" and not (0 <= val <= 365):
                    raise IntakeValidationError("Days must be between 0 and 365.")
                if question.question_id == "symptom_severity" and not (1 <= val <= 10):
                    raise IntakeValidationError("Severity must be between 1 and 10.")
                return val
            except (ValueError, TypeError):
                raise IntakeValidationError(f"Please provide a valid number for {question.question_id}.")
        
        if question.input_type == "yes_no":
            if str(answer).lower() in ["yes", "y", "true", "1"]:
                return True
            if str(answer).lower() in ["no", "n", "false", "0"]:
                return False
            raise IntakeValidationError("Please answer with 'yes' or 'no'.")

        if question.input_type == "multi_select":
            if isinstance(answer, str):
                answers = [a.strip().lower() for a in answer.split(",")]
            elif isinstance(answer, list):
                answers = [str(a).strip().lower() for a in answer]
            else:
                answers = [str(answer).strip().lower()]
            
            # Deduplicate
            answers = list(dict.fromkeys(answers))
            
            if not answers or answers == [""]:
                raise IntakeValidationError("Please select at least one option.")
            
            if question.options:
                allowed_options = [o.lower() for o in question.options]
                invalid = [a for a in answers if a not in allowed_options]
                if invalid:
                    raise IntakeValidationError(f"Invalid options: {', '.join(invalid)}")
            return answers

        return answer

    def _check_and_advance_stage(self, session: SessionState) -> None:
        """Advances intake stage if current stage questions are all answered."""
        questions = QUESTION_TREE.get(session.intake_stage, [])
        if all(self._is_answered(session, q) for q in questions):
            next_stage_map = {
                IntakeStage.DEMOGRAPHICS: IntakeStage.SYMPTOMS,
                IntakeStage.SYMPTOMS: IntakeStage.HISTORY,
                IntakeStage.HISTORY: IntakeStage.COMPLETE
            }
            if session.intake_stage in next_stage_map:
                session.intake_stage = next_stage_map[session.intake_stage]

    def _find_question_by_id(self, question_id: str) -> Optional[IntakeQuestion]:
        """Helper to find a question in the tree by ID."""
        for stage_questions in QUESTION_TREE.values():
            for q in stage_questions:
                if q.question_id == question_id:
                    return q
        return None
