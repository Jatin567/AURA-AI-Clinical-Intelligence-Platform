import pytest
from datetime import datetime, timezone, timedelta
from app.models.session import SessionState, PatientProfile
from app.models.triage import TriageLevel
from app.otc_suggester import OTCSuggester

@pytest.fixture
def suggester():
    return OTCSuggester()

@pytest.fixture
def base_session():
    now = datetime.now(timezone.utc)
    return SessionState(
        session_id="test-session-otc",
        created_at=now,
        expires_at=now + timedelta(hours=2),
        patient_profile=PatientProfile(age=30, sex="female"),
    )

def test_gate1_emergency_short_circuit(suggester, base_session):
    """Gate 1: EMERGENCY triage returns empty suggestions immediately."""
    candidates = ["ibuprofen"]
    result = suggester.validate(base_session, candidates, TriageLevel.EMERGENCY)
    assert result.suggestions == []
    assert result.triage_level_at_evaluation == TriageLevel.EMERGENCY

def test_gate1_urgent_short_circuit(suggester, base_session):
    """Gate 1: URGENT triage returns empty suggestions immediately."""
    candidates = ["ibuprofen"]
    result = suggester.validate(base_session, candidates, TriageLevel.URGENT)
    assert result.suggestions == []

def test_gate2_unknown_drug_rejected(suggester, base_session):
    """Gate 2: Unknown drug rejected."""
    candidates = ["mystery_pill"]
    result = suggester.validate(base_session, candidates, TriageLevel.ROUTINE)
    assert len(result.suggestions) == 1
    assert result.suggestions[0].approved is False
    assert result.suggestions[0].rejection_reason == "Not in approved OTC allowlist"

def test_gate3_age_rejection(suggester, base_session):
    """Gate 3: Age-restricted drug rejected."""
    # Diphenhydramine is now safe_for_ages_above=12
    base_session.patient_profile.age = 10
    candidates = ["diphenhydramine"]
    result = suggester.validate(base_session, candidates, TriageLevel.ROUTINE)
    assert result.suggestions[0].approved is False
    assert "Not recommended for age 10" in result.suggestions[0].rejection_reason

def test_gate4_condition_rejection(suggester, base_session):
    """Gate 4: Contraindicated condition correctly blocks drug."""
    # Ibuprofen contraindicated for "Heart disease"
    base_session.patient_profile.known_conditions = ["Heart disease"]
    candidates = ["ibuprofen"]
    result = suggester.validate(base_session, candidates, TriageLevel.ROUTINE)
    assert result.suggestions[0].approved is False
    assert "due to condition: Heart disease" in result.suggestions[0].rejection_reason

def test_gate4_medication_rejection(suggester, base_session):
    """Gate 4: Contraindicated medication correctly blocks drug."""
    # Ibuprofen contraindicated for "Warfarin"
    base_session.patient_profile.current_medications = ["Warfarin"]
    candidates = ["ibuprofen"]
    result = suggester.validate(base_session, candidates, TriageLevel.ROUTINE)
    assert result.suggestions[0].approved is False
    assert "due to medication: Warfarin" in result.suggestions[0].rejection_reason

def test_successful_approval(suggester, base_session):
    """Test clean patient profile with valid drug returns approved suggestion."""
    candidates = ["ibuprofen"]
    result = suggester.validate(base_session, candidates, TriageLevel.ROUTINE)
    assert result.suggestions[0].approved is True
    assert result.suggestions[0].medicine.name == "Ibuprofen"
    assert result.suggestions[0].rejection_reason is None

def test_case_insensitivity(suggester, base_session):
    """Test case-insensitive matching for candidates and contraindications."""
    # Use "IBUPROFEN" candidate and patient has "stomach ULCER"
    base_session.patient_profile.known_conditions = ["stomach ULCER"]
    candidates = [" IBUPROFEN "]
    result = suggester.validate(base_session, candidates, TriageLevel.ROUTINE)
    
    # ibuprofen exists in allowlist (Gate 2 success)
    # Rejection should happen at Gate 4 because "stomach ulcer" matches "stomach ULCER"
    assert result.suggestions[0].approved is False
    assert "due to condition: Stomach ulcer" in result.suggestions[0].rejection_reason

def test_multiple_candidates(suggester, base_session):
    """Verify multiple candidates are evaluated correctly."""
    # Ibuprofen (OK), mystery (Reject), Acetaminophen (OK)
    candidates = ["ibuprofen", "mystery", "acetaminophen"]
    result = suggester.validate(base_session, candidates, TriageLevel.ROUTINE)
    assert len(result.suggestions) == 3
    assert result.suggestions[0].approved is True
    assert result.suggestions[1].approved is False
    assert result.suggestions[2].approved is True
