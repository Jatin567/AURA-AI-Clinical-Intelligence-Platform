import pytest
from datetime import datetime, timezone, timedelta
from app.models.session import SessionState, PatientProfile
from app.models.red_flag import RedFlagResult, RedFlagMatch, RedFlagSeverity
from app.models.triage import TriageLevel
from app.severity_classifier import SeverityClassifier

@pytest.fixture
def classifier():
    return SeverityClassifier()

@pytest.fixture
def empty_session():
    now = datetime.now(timezone.utc)
    return SessionState(
        session_id="test-session",
        created_at=now,
        expires_at=now + timedelta(hours=2),
        patient_profile=PatientProfile()
    )

@pytest.fixture
def empty_red_flag_result():
    return RedFlagResult(
        evaluated_at=datetime.now(timezone.utc),
        flags_matched=[],
        highest_severity=None,
        input_snapshot={}
    )

def test_rule1_emergency_hard_gate(classifier, empty_session):
    """Rule 1: EMERGENCY hard gate overrides all other signals."""
    red_flag_result = RedFlagResult(
        evaluated_at=datetime.now(timezone.utc),
        flags_matched=[
            RedFlagMatch(
                rule_id="chest_pain",
                severity=RedFlagSeverity.EMERGENCY,
                matched_on="chest pain",
                explanation="Chest pain can be a sign of a heart attack.",
                rule_description="Test rule"
            )
        ],
        highest_severity=RedFlagSeverity.EMERGENCY,
        input_snapshot={}
    )
    
    # Even with low severity symptoms, it should be EMERGENCY
    empty_session.symptom_severity = 2
    decision = classifier.classify(empty_session, red_flag_result)
    
    assert decision.triage_level == TriageLevel.EMERGENCY
    assert decision.confidence == "high"
    assert "heart attack" in decision.primary_reason
    assert decision.classification_version == "1.0"

def test_rule2_urgent_red_flag(classifier, empty_session):
    """Rule 2: URGENT from red flag result."""
    red_flag_result = RedFlagResult(
        evaluated_at=datetime.now(timezone.utc),
        flags_matched=[
            RedFlagMatch(
                rule_id="high_severity",
                severity=RedFlagSeverity.URGENT,
                matched_on="9",
                explanation="High severity self-report.",
                rule_description="Test rule"
            )
        ],
        highest_severity=RedFlagSeverity.URGENT,
        input_snapshot={}
    )
    
    decision = classifier.classify(empty_session, red_flag_result)
    
    assert decision.triage_level == TriageLevel.URGENT
    assert decision.confidence == "high"
    assert "clinical red flags" in decision.primary_reason
    assert any("High severity" in f for f in decision.contributing_factors)

def test_rule3_urgent_acute_high_severity(classifier, empty_session, empty_red_flag_result):
    """Rule 3: URGENT from severity >= 7 AND acute onset."""
    empty_session.symptom_severity = 8
    # FIX: Acute onset keywords must now be in chief_complaint
    empty_session.chief_complaint = "Sudden onset of severe pain"
    empty_session.symptom_duration = "started today"
    
    decision = classifier.classify(empty_session, empty_red_flag_result)
    
    assert decision.triage_level == TriageLevel.URGENT
    assert decision.confidence == "medium"
    assert "acute onset" in decision.primary_reason.lower()

def test_rule4_urgent_known_condition(classifier, empty_session, empty_red_flag_result):
    """Rule 4: URGENT from known condition interaction (severity >= 6)."""
    empty_session.patient_profile.known_conditions = ["Diabetes"]
    empty_session.symptom_severity = 6
    empty_session.symptom_duration = "A few days" # Not acute
    
    decision = classifier.classify(empty_session, empty_red_flag_result)
    
    assert decision.triage_level == TriageLevel.URGENT
    assert decision.confidence == "medium"
    assert "Diabetes" in decision.primary_reason

def test_rule5_routine_severity(classifier, empty_session, empty_red_flag_result):
    """Rule 5: ROUTINE from severity 4-6."""
    empty_session.symptom_severity = 5
    empty_session.symptom_duration = "A few weeks"
    
    decision = classifier.classify(empty_session, empty_red_flag_result)
    
    assert decision.triage_level == TriageLevel.ROUTINE
    assert decision.confidence == "medium"
    assert "Moderate symptoms" in decision.primary_reason

def test_rule5_routine_duration_keywords(classifier, empty_session, empty_red_flag_result):
    """Rule 5: ROUTINE from duration keywords."""
    empty_session.symptom_severity = 3
    empty_session.symptom_duration = "For two weeks"
    
    decision = classifier.classify(empty_session, empty_red_flag_result)
    
    assert decision.triage_level == TriageLevel.ROUTINE
    assert decision.confidence == "medium"
    assert "chronic duration" in decision.primary_reason

def test_rule6_home_care_default(classifier, empty_session, empty_red_flag_result):
    """Rule 6: HOME_CARE default."""
    empty_session.symptom_severity = 2
    empty_session.symptom_duration = "Since this morning" # Low severity, not high enough for acute urgent
    
    decision = classifier.classify(empty_session, empty_red_flag_result)
    
    assert decision.triage_level == TriageLevel.HOME_CARE
    assert decision.confidence == "medium"

def test_rule6_home_care_no_severity(classifier, empty_session, empty_red_flag_result):
    """Rule 6: HOME_CARE with low confidence when severity is None."""
    empty_session.symptom_severity = None
    
    decision = classifier.classify(empty_session, empty_red_flag_result)
    
    assert decision.triage_level == TriageLevel.HOME_CARE
    assert decision.confidence == "low"

def test_exception_fallback(classifier, empty_session, empty_red_flag_result):
    """Test that it recovers from exceptions."""
    # Force an exception by passing partial red_flag_result (missing flags_matched)
    decision = classifier.classify(empty_session, None)
    
    assert decision.triage_level == TriageLevel.URGENT
    assert decision.confidence == "low"
    assert "Classification error" in decision.primary_reason

def test_contributing_factors_multi_signal(classifier, empty_session, empty_red_flag_result):
    """Verify contributing_factors is populated."""
    empty_session.symptom_severity = 5
    empty_session.symptom_duration = "3 weeks"
    
    decision = classifier.classify(empty_session, empty_red_flag_result)
    
    # Should be ROUTINE
    assert len(decision.contributing_factors) == 2
    assert any("Moderate severity" in f for f in decision.contributing_factors)
    assert any("Symptoms persistent" in f for f in decision.contributing_factors)
