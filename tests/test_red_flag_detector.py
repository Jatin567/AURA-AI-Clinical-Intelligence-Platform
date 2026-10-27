import pytest
import os
import json
import asyncio
from datetime import datetime, timezone
from app.models.session import SessionState, PatientProfile, IntakeStage
from app.models.red_flag import RedFlagSeverity, RedFlagResult
from app.red_flag_detector import RedFlagDetector
from app.audit_logger import log_red_flag_evaluation


@pytest.fixture
def detector():
    return RedFlagDetector()


@pytest.fixture
def empty_session():
    return SessionState(
        session_id="test-session",
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        intake_stage=IntakeStage.COMPLETE,
        patient_profile=PatientProfile(age=30),
        chief_complaint=None,
        symptoms=[],
        conversation_history=[]
    )


def test_clean_session(detector, empty_session):
    """Test that a clean session returns no red flags."""
    empty_session.chief_complaint = "I feel fine."
    result = detector.evaluate(empty_session)
    assert result.highest_severity is None
    assert len(result.flags_matched) == 0


def test_chest_pain_rule(detector, empty_session):
    """Test chest pain detection."""
    empty_session.chief_complaint = "I have some chest tightness."
    result = detector.evaluate(empty_session)
    assert result.highest_severity == RedFlagSeverity.EMERGENCY
    assert any(m.rule_id == "chest_pain" for m in result.flags_matched)


def test_breathing_rule(detector, empty_session):
    """Test breathing difficulty detection."""
    empty_session.symptoms = ["shortness of breath"]
    result = detector.evaluate(empty_session)
    assert result.highest_severity == RedFlagSeverity.EMERGENCY
    assert any(m.rule_id == "breathing_difficulty" for m in result.flags_matched)


def test_stroke_signs_rule(detector, empty_session):
    """Test stroke signs detection."""
    empty_session.chief_complaint = "Worst headache of my life"
    result = detector.evaluate(empty_session)
    assert result.highest_severity == RedFlagSeverity.EMERGENCY
    assert any(m.rule_id == "stroke_signs" for m in result.flags_matched)


def test_loss_of_consciousness_rule(detector, empty_session):
    """Test loss of consciousness detection."""
    empty_session.chief_complaint = "I fainted earlier."
    result = detector.evaluate(empty_session)
    assert result.highest_severity == RedFlagSeverity.EMERGENCY
    assert any(m.rule_id == "loss_of_consciousness" for m in result.flags_matched)


def test_severe_bleeding_rule(detector, empty_session):
    """Test severe bleeding detection."""
    empty_session.symptoms = ["uncontrolled bleeding from arm"]
    result = detector.evaluate(empty_session)
    assert result.highest_severity == RedFlagSeverity.EMERGENCY
    assert any(m.rule_id == "severe_bleeding" for m in result.flags_matched)


def test_infant_fever_rule(detector, empty_session):
    """Test infant fever rule logic."""
    # is_infant=True with fever -> EMERGENCY
    empty_session.patient_profile.is_infant = True
    empty_session.chief_complaint = "The baby has a fever."
    result = detector.evaluate(empty_session)
    assert result.highest_severity == RedFlagSeverity.EMERGENCY
    assert any(m.rule_id == "infant_fever" for m in result.flags_matched)

    # is_infant=False with fever (even if age is 2) -> None
    empty_session.patient_profile.is_infant = False
    empty_session.patient_profile.age = 2
    result = detector.evaluate(empty_session)
    assert result.highest_severity is None
    assert len(result.flags_matched) == 0


def test_high_severity_rule(detector, empty_session):
    """Test high severity score detection."""
    empty_session.symptom_severity = 9
    result = detector.evaluate(empty_session)
    assert result.highest_severity == RedFlagSeverity.URGENT
    assert any(m.rule_id == "high_severity_score" for m in result.flags_matched)
    assert "score of 9/10" in result.flags_matched[0].explanation


def test_mental_health_crisis_rule(detector, empty_session):
    """Test mental health crisis detection and crisis resource flag."""
    empty_session.chief_complaint = "I want to die"
    result = detector.evaluate(empty_session)
    assert result.highest_severity == RedFlagSeverity.EMERGENCY
    match = next(m for m in result.flags_matched if m.rule_id == "mental_health_crisis")
    assert match.requires_immediate_crisis_resource is True


def test_mental_health_crisis_resource_flag(detector, empty_session):
    """Specific test for suicidal ideation triggering crisis resource flag."""
    empty_session.chief_complaint = "I am suicidal"
    result = detector.evaluate(empty_session)
    match = next(m for m in result.flags_matched if m.rule_id == "mental_health_crisis")
    assert match.requires_immediate_crisis_resource is True


def test_multiple_rules_firing(detector, empty_session):
    """Test that multiple rules can fire simultaneously."""
    empty_session.chief_complaint = "I have chest pain and shortness of breath."
    result = detector.evaluate(empty_session)
    assert result.highest_severity == RedFlagSeverity.EMERGENCY
    rule_ids = [m.rule_id for m in result.flags_matched]
    assert "chest_pain" in rule_ids
    assert "breathing_difficulty" in rule_ids


def test_substring_matches(detector, empty_session):
    """Test that partial phrase matches work."""
    empty_session.chief_complaint = "I have chest pain that comes and goes"
    result = detector.evaluate(empty_session)
    assert any(m.rule_id == "chest_pain" for m in result.flags_matched)


def test_input_snapshot_capture(detector, empty_session):
    """Test that input_snapshot in the result contains the exact values evaluated."""
    empty_session.chief_complaint = "Chest pain"
    empty_session.symptom_severity = 10
    empty_session.patient_profile.age = 45
    
    result = detector.evaluate(empty_session)
    snapshot = result.input_snapshot
    assert snapshot["chief_complaint"] == "Chest pain"
    assert snapshot["symptom_severity"] == 10
    assert snapshot["patient_profile"]["age"] == 45


@pytest.mark.asyncio
async def test_audit_logging(detector, empty_session):
    """Verifies that audit logging works. Note: on Windows file removal may fail if logger is active."""
    empty_session.chief_complaint = "Chest pain"
    result = detector.evaluate(empty_session)
    
    log_file = "logs/red_flag_audit.log"
    
    # Just record the current line count or just verify the last line after logging
    await log_red_flag_evaluation(empty_session.session_id, result)
    
    assert os.path.exists(log_file)
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) > 0
        record = json.loads(lines[-1])
        assert record["session_id"] == "test-session"
        assert record["highest_severity"] == "EMERGENCY"
        assert len(record["flags_matched"]) > 0
