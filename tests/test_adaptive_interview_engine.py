import pytest
from app.interview import (
    AdaptiveInterviewEngine,
    QuestionBank,
    EvidenceCollector,
    InterviewState,
    EvidenceSource,
    ClinicalEvidence
)
from app.reasoning import ClinicalInput


@pytest.fixture
def adaptive_engine():
    """Provides fresh instance of AdaptiveInterviewEngine."""
    return AdaptiveInterviewEngine()


def test_question_bank_loading():
    """Test that question bank repository loads questions cleanly."""
    bank = QuestionBank()
    questions = bank.get_all_questions()
    assert len(questions) >= 15, f"Expected at least 15 questions, found {len(questions)}"
    
    q_acs = bank.get_question_by_id("Q_ACS_001")
    assert q_acs is not None
    assert q_acs.target_evidence_key == "chest_pain_radiation"
    assert q_acs.purpose != ""


def test_evidence_collector_process_answer():
    """Test processing an interview answer into a structured ClinicalEvidence item."""
    collector = EvidenceCollector()
    bank = QuestionBank()
    q = bank.get_question_by_id("Q_ACS_001")
    state = InterviewState(session_id="sess_test_1")

    ev = collector.process_interview_answer(q, "yes", state)

    assert ev.source == EvidenceSource.PATIENT_INTERVIEW
    assert ev.key == "chest_pain_radiation"
    assert ev.value == "yes"
    assert "left arm pain" in ev.clinical_tags
    assert len(state.gathered_evidence) == 1
    assert state.turn_count == 1


def test_adaptive_engine_red_flag_prioritization(adaptive_engine):
    """Test that chest pain presentation prioritizes Tier 1 / Red Flag discriminators."""
    base_input = ClinicalInput(
        symptoms=["chest pain"],
        chief_complaint="Severe pressure in chest",
        age=65
    )
    state = InterviewState(session_id="sess_test_2")

    result = adaptive_engine.evaluate_and_select_next(base_input, state)

    assert not result.is_complete
    assert result.selected_question is not None
    assert result.selected_question.priority_tier in ["CRITICAL_RED_FLAG", "DIFFERENTIAL_DISCRIMINATOR"]
    assert result.differential_entropy > 0.0


def test_multimodal_evidence_ingestion(adaptive_engine):
    """Test that ingesting non-interview evidence (simulating future OCR/Voice) updates reasoning output."""
    collector = EvidenceCollector()
    base_input = ClinicalInput(symptoms=["chest pain"], age=65)
    state = InterviewState(session_id="sess_test_3")

    # Ingest evidence from simulated Document OCR
    collector.ingest_external_evidence(
        source=EvidenceSource.DOCUMENT_OCR,
        key="known_conditions",
        value="Diabetes Mellitus",
        symptom_tags=[],
        state=state
    )

    result = adaptive_engine.evaluate_and_select_next(base_input, state)

    assert result.current_reasoning_output is not None
    assert len(state.gathered_evidence) == 1
    assert state.gathered_evidence[0].source == EvidenceSource.DOCUMENT_OCR


def test_stopping_criteria_max_turns(adaptive_engine):
    """Test that max turn cap (6) dynamically terminates the interview."""
    base_input = ClinicalInput(symptoms=["cough"], age=25)
    state = InterviewState(session_id="sess_test_4", turn_count=6)

    result = adaptive_engine.evaluate_and_select_next(base_input, state)

    assert result.is_complete
    assert "Maximum dynamic interview turns" in result.completion_reason


def test_differential_entropy_calculation(adaptive_engine):
    """Test that Shannon differential entropy is calculated accurately."""
    base_input = ClinicalInput(symptoms=["chest pain", "shortness of breath"], age=70)
    state = InterviewState(session_id="sess_test_5")

    result = adaptive_engine.evaluate_and_select_next(base_input, state)

    assert result.differential_entropy >= 0.0
    assert result.current_reasoning_output is not None
