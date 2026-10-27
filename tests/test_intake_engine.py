import pytest
from datetime import datetime, timezone, timedelta
from app.models.session import SessionState, IntakeStage, PatientProfile
from app.intake_engine import IntakeEngine, IntakeValidationError


@pytest.fixture
def intake_engine():
    return IntakeEngine()


@pytest.fixture
def empty_session():
    now = datetime.now(timezone.utc)
    return SessionState(
        session_id="test-session",
        created_at=now,
        expires_at=now + timedelta(hours=2),
        intake_stage=IntakeStage.DEMOGRAPHICS,
        patient_profile=PatientProfile(),
        symptoms=[],
        conversation_history=[]
    )


def test_get_first_question(intake_engine, empty_session):
    """Verifies that the first question returned is 'age'."""
    question = intake_engine.get_next_question(empty_session)
    assert question is not None
    assert question.question_id == "age"
    assert question.field_target == "patient_profile.age"


def test_process_answer_valid_age(intake_engine, empty_session):
    """Verifies that a valid age is correctly mapped to the session."""
    intake_engine.process_answer(empty_session, "25")
    assert empty_session.patient_profile.age == 25
    assert len(empty_session.conversation_history) == 1
    assert empty_session.conversation_history[0]["question_id"] == "age"
    assert empty_session.conversation_history[0]["answer"] == "25"


def test_process_answer_invalid_age(intake_engine, empty_session):
    """Verifies that an invalid age raises IntakeValidationError."""
    with pytest.raises(IntakeValidationError) as excinfo:
        intake_engine.process_answer(empty_session, "150")
    assert "Age must be between 0 and 120" in str(excinfo.value)


def test_stage_advancement_demographics_to_symptoms(intake_engine, empty_session):
    """Verifies that the stage advances to symptoms after demographics are completed."""
    # Answer all demographics
    intake_engine.process_answer(empty_session, "30")       # age
    intake_engine.process_answer(empty_session, "male")     # sex
    intake_engine.process_answer(empty_session, "none")     # known_conditions
    intake_engine.process_answer(empty_session, "none")     # medications
    intake_engine.process_answer(empty_session, "none")     # allergies
    
    assert empty_session.intake_stage == IntakeStage.SYMPTOMS
    
    # Next question should be from symptoms stage
    next_q = intake_engine.get_next_question(empty_session)
    assert next_q.question_id == "chief_complaint"


def test_is_intake_complete(intake_engine, empty_session):
    """Verifies is_intake_complete logic across the flow."""
    engine = intake_engine
    session = empty_session
    
    assert not engine.is_intake_complete(session)
    
    # Demographics
    engine.process_answer(session, "30")
    engine.process_answer(session, "female")
    engine.process_answer(session, "none")
    engine.process_answer(session, "none")
    engine.process_answer(session, "none")
    
    assert not engine.is_intake_complete(session)
    assert session.intake_stage == IntakeStage.SYMPTOMS
    
    # Symptoms
    engine.process_answer(session, "Headache")              # chief
    engine.process_answer(session, "2 days")                # duration
    engine.process_answer(session, "7")                     # severity
    engine.process_answer(session, "nausea, fatigue")       # associated
    
    assert not engine.is_intake_complete(session)
    assert session.intake_stage == IntakeStage.HISTORY
    
    # History
    engine.process_answer(session, "Rest")                  # better
    engine.process_answer(session, "Light")                 # worse
    engine.process_answer(session, "No")                    # before
    
    assert session.intake_stage == IntakeStage.COMPLETE
    assert engine.is_intake_complete(session)


def test_symptom_field_replacement(intake_engine, empty_session):
    """Verifies that re-answering a question replaces the value instead of appending."""
    # Move to symptoms stage
    empty_session.intake_stage = IntakeStage.SYMPTOMS
    
    # Answer chief complaint
    intake_engine.process_answer(empty_session, "Headache")
    assert empty_session.chief_complaint == "Headache"
    assert len(empty_session.conversation_history) == 1
    
    # Correct chief complaint
    intake_engine.process_answer(empty_session, "Migraine", question_id="chief_complaint")
    assert empty_session.chief_complaint == "Migraine"
    assert len(empty_session.conversation_history) == 1
    assert empty_session.conversation_history[0]["answer"] == "Migraine"
    
    # Multi-select (associated symptoms)
    intake_engine.process_answer(empty_session, "fever, nausea", question_id="associated_symptoms")
    assert empty_session.symptoms == ["fever", "nausea"]
    assert len(empty_session.conversation_history) == 2
    
    # Correct multi-select
    intake_engine.process_answer(empty_session, "dizziness", question_id="associated_symptoms")
    assert empty_session.symptoms == ["dizziness"]
    assert len(empty_session.conversation_history) == 2
    assert empty_session.conversation_history[1]["answer"] == "['dizziness']"


def test_severity_validation(intake_engine, empty_session):
    """Verifies severity scaling validation."""
    # Skip demographics to get to symptoms
    empty_session.intake_stage = IntakeStage.SYMPTOMS
    empty_session.patient_profile.age = 30
    empty_session.patient_profile.sex = "male"
    
    # chief
    intake_engine.process_answer(empty_session, "Cough")
    # duration
    intake_engine.process_answer(empty_session, "1 week")
    
    # severity invalid
    with pytest.raises(IntakeValidationError) as excinfo:
        intake_engine.process_answer(empty_session, "11")
    assert "Severity must be between 1 and 10" in str(excinfo.value)
    
    # severity valid
    intake_engine.process_answer(empty_session, "5")
    assert empty_session.symptom_severity == 5


def test_get_next_question_when_complete(intake_engine, empty_session):
    """Verifies that IntakeAlreadyCompleteError is raised when intake is complete."""
    from app.intake_engine import IntakeAlreadyCompleteError
    empty_session.intake_stage = IntakeStage.COMPLETE
    with pytest.raises(IntakeAlreadyCompleteError):
        intake_engine.get_next_question(empty_session)


def test_text_answer_length_validation(intake_engine, empty_session):
    """Verifies that text answers exceeding 1000 characters raise IntakeValidationError."""
    long_answer = "a" * 1001
    with pytest.raises(IntakeValidationError) as excinfo:
        intake_engine.process_answer(empty_session, long_answer)
    assert "Answer exceeds maximum length of 1000 characters" in str(excinfo.value)


def test_multi_select_hardening(intake_engine, empty_session):
    """Verifies strict multi-select parsing and validation."""
    # known_conditions is a multi_select with options: ["diabetes", "hypertension", "asthma", "none"]
    # We need to get past age and sex
    intake_engine.process_answer(empty_session, "30")
    intake_engine.process_answer(empty_session, "male")
    
    # 1. Whitespace and case-insensitivity
    empty_session.patient_profile.known_conditions = [] # Ensure it's treated as unanswered
    intake_engine.process_answer(empty_session, "  DIABETES, asthma  ")
    assert empty_session.patient_profile.known_conditions == ["diabetes", "asthma"]
    
    # 2. Deduplication
    empty_session.patient_profile.known_conditions = []
    intake_engine.process_answer(empty_session, "diabetes, diabetes, asthma, DIABETES")
    assert empty_session.patient_profile.known_conditions == ["diabetes", "asthma"]
    
    # 3. Strict rejection of invalid options
    empty_session.patient_profile.known_conditions = []
    with pytest.raises(IntakeValidationError) as excinfo:
        intake_engine.process_answer(empty_session, "asthma, lupus, none")
    assert "Invalid options: lupus" in str(excinfo.value)
    
    # 4. Even if "none" is present, invalid options should trigger rejection
    empty_session.patient_profile.known_conditions = []
    with pytest.raises(IntakeValidationError) as excinfo:
        intake_engine.process_answer(empty_session, "none, unknown")
    assert "Invalid options: unknown" in str(excinfo.value)


def test_multi_select_empty_answer(intake_engine, empty_session):
    """Verifies that empty or blank multi-select answers are rejected."""
    # known_conditions is a multi_select
    intake_engine.process_answer(empty_session, "30")
    intake_engine.process_answer(empty_session, "male")
    
    with pytest.raises(IntakeValidationError) as excinfo:
        intake_engine.process_answer(empty_session, "")
    assert "Please select at least one option" in str(excinfo.value)
    
    with pytest.raises(IntakeValidationError) as excinfo:
        intake_engine.process_answer(empty_session, "   ")
    assert "Please select at least one option" in str(excinfo.value)


def test_infant_question_trigger(intake_engine, empty_session):
    """Verifies that is_infant_under_3_months is asked ONLY when age is 0."""
    # Age 30 -> should skip to sex
    intake_engine.process_answer(empty_session, "30")
    next_q = intake_engine.get_next_question(empty_session)
    assert next_q.question_id == "sex"
    
    # New session, Age 0 -> should ask infant question
    now = datetime.now(timezone.utc)
    session_0 = SessionState(
        session_id="infant-session",
        created_at=now,
        expires_at=now + timedelta(hours=2),
        intake_stage=IntakeStage.DEMOGRAPHICS,
        patient_profile=PatientProfile()
    )
    intake_engine.process_answer(session_0, "0")
    next_q = intake_engine.get_next_question(session_0)
    assert next_q.question_id == "age_in_days"
    
    # Answer 14 days
    intake_engine.process_answer(session_0, "14")
    assert session_0.patient_profile.age_in_days == 14
    
    next_q = intake_engine.get_next_question(session_0)
    assert next_q.question_id == "is_infant_under_3_months"
    
    # Answer YES
    intake_engine.process_answer(session_0, "yes")
    assert session_0.patient_profile.is_infant is True
    next_q = intake_engine.get_next_question(session_0)
    assert next_q.question_id == "sex"
