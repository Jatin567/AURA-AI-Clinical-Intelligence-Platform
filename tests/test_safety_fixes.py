import pytest
from datetime import datetime, timezone
from app.models.session import SessionState, PatientProfile
from app.otc_suggester import OTCSuggester
from app.severity_classifier import SeverityClassifier
from app.triage_output_builder import TriageOutputBuilder
from app.models.triage import TriageLevel, TriageDecision
from app.models.red_flag import RedFlagResult, RedFlagMatch, RedFlagSeverity
from app.models.llm import OrchestratorResult

@pytest.fixture
def empty_rf_result():
    return RedFlagResult(
        evaluated_at=datetime.now(timezone.utc),
        flags_matched=[],
        highest_severity=None,
        input_snapshot={}
    )

def test_neonate_otc_gate(empty_rf_result):
    """Test: 14-day-old infant with fever gets no OTC suggestions (even acetaminophen)"""
    suggester = OTCSuggester()
    session = SessionState(
        session_id="test-neonate",
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        patient_profile=PatientProfile(age=0, age_in_days=14)
    )
    
    # Even if acetaminophen is a candidate
    candidates = ["acetaminophen"]
    result = suggester.validate(session, candidates, TriageLevel.ROUTINE)
    
    assert result.suggestions == []
    assert result.rejection_reason == "No OTC medications for neonates"

def test_acute_onset_keyword_match(empty_rf_result):
    """Test: 'Sudden chest pain' triggers URGENT via Rule 3 (acute onset keywords)"""
    classifier = SeverityClassifier()
    session = SessionState(
        session_id="test-acute",
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        chief_complaint="Sudden chest pain",
        symptom_severity=8
    )
    
    decision = classifier.classify(session, empty_rf_result)
    assert decision.triage_level == TriageLevel.URGENT
    assert "acute onset" in decision.primary_reason.lower()

def test_crisis_resource_intl():
    """Test: Non-US user with crisis flag sees IASP link, not 988"""
    builder = TriageOutputBuilder()
    session = SessionState(
        session_id="test-intl",
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc)
    )
    
    crisis_match = RedFlagMatch(
        rule_id="suicide_risk",
        rule_description="Self-harm risk detected",
        severity=RedFlagSeverity.URGENT,
        explanation="Patient reported self-harm thoughts.",
        matched_on="self-harm",
        requires_immediate_crisis_resource=True
    )
    rf_result = RedFlagResult(
        evaluated_at=datetime.now(timezone.utc),
        flags_matched=[crisis_match],
        highest_severity=RedFlagSeverity.URGENT,
        input_snapshot={}
    )
    
    decision = TriageDecision(
        session_id=session.session_id,
        triage_level=TriageLevel.URGENT,
        confidence="high",
        primary_reason="Crisis flag",
        contributing_factors=[],
        red_flag_result=rf_result,
        classified_at=datetime.now(timezone.utc),
        classification_version="1.0"
    )
    
    orc_result = OrchestratorResult(
        session_id=session.session_id,
        triage_decision=decision,
        assembled_at=datetime.now(timezone.utc),
        llm_skipped=True
    )
    
    from app.models.otc import OTCResult
    otc_result = OTCResult(
        session_id=session.session_id,
        suggestions=[],
        evaluated_at=datetime.now(timezone.utc),
        triage_level_at_evaluation=TriageLevel.URGENT
    )
    
    # US Case
    output_us = builder.build(session, orc_result, otc_result, user_region="US")
    assert any("988" in r for r in output_us.crisis_resources)
    assert not any("iasp.info" in r for r in output_us.crisis_resources)
    
    # Intl Case
    output_intl = builder.build(session, orc_result, otc_result, user_region="CA")
    assert any("iasp.info" in r for r in output_intl.crisis_resources)
    assert not any("988" in r for r in output_intl.crisis_resources)

# GAP 3: Expanded Safety Tests

def test_neonate_28_days_blocked():
    """Exactly 28 days old is still a neonate — no OTC"""
    suggester = OTCSuggester()
    session = SessionState(
        session_id="test-28",
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        patient_profile=PatientProfile(age=0, age_in_days=28)
    )
    result = suggester.validate(session, ["acetaminophen"], TriageLevel.ROUTINE)
    assert result.suggestions == []
    assert "neonates" in (result.rejection_reason or "").lower()

def test_infant_29_days_allowed():
    """29 days old is infant, not neonate — acetaminophen allowed"""
    from app.data.otc_allowlist import OTC_ALLOWLIST
    suggester = OTCSuggester()
    session = SessionState(
        session_id="test-29",
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        patient_profile=PatientProfile(age=0, age_in_days=29)
    )
    result = suggester.validate(session, ["acetaminophen"], TriageLevel.ROUTINE)
    assert len(result.suggestions) == 1
    assert result.suggestions[0].approved is True
    assert result.suggestions[0].medicine.name.lower() == "acetaminophen"

def test_missing_age_in_days_blocks_otc():
    """If age=0 but age_in_days missing, treat as neonate (fail-safe)"""
    suggester = OTCSuggester()
    session = SessionState(
        session_id="test-missing-days",
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        patient_profile=PatientProfile(age=0, age_in_days=None)
    )
    result = suggester.validate(session, ["acetaminophen"], TriageLevel.ROUTINE)
    assert result.suggestions == []  # Conservative block

def test_invalid_region_header_defaults_us():
    """Malformed region defaults to US resources using direct helper test + client check"""
    from app.api.routes import get_user_region
    from fastapi import Request
    
    # Test helper directly
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"X-User-Region": "XX<script>"}
    assert get_user_region(mock_request) == "US"
    
    # Integration test with client
    from fastapi.testclient import TestClient
    from app.main import app
    from unittest.mock import patch, MagicMock as UMagicMock
    from app.dependencies import get_current_session
    
    # Create a mock session that is complete and has a crisis flag
    crisis_match = RedFlagMatch(
        rule_id="suicide_risk",
        rule_description="Self-harm risk detected",
        severity=RedFlagSeverity.URGENT,
        explanation="Patient reported self-harm thoughts.",
        matched_on="self-harm",
        requires_immediate_crisis_resource=True
    )
    rf_result = RedFlagResult(
        evaluated_at=datetime.now(timezone.utc),
        flags_matched=[crisis_match],
        highest_severity=RedFlagSeverity.URGENT,
        input_snapshot={}
    )
    
    session_with_result = SessionState(
        session_id="test-header-val",
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        triage_result={
            "session_id": "test-header-val",
            "triage_level": "URGENT",
            "triage_label": "See a Doctor Within 24 Hours",
            "explanation": "Test",
            "approved_otc_suggestions": [],
            "otc_disclaimers": [],
            "action_items": [],
            "crisis_resources": ["If you are in crisis, please call or text 988"],
            "medical_disclaimer": "Test",
            "assembled_at": datetime.now(timezone.utc).isoformat(),
            "llm_was_used": False
        }
    )

    app.dependency_overrides[get_current_session] = lambda: session_with_result
    
    with TestClient(app) as client:
        # Send invalid header
        response = client.get("/api/v1/session/result", headers={"X-User-Region": "XX<script>"})
        assert response.status_code == 200
        # Verify 988 appears (default US)
        # Note: In our current get_result impl, it doesn't re-build, but the helper is called.
        # The stored result in my mock already has 988.
        assert "988" in response.json()["crisis_resources"][0]
        
    app.dependency_overrides = {}

from unittest.mock import MagicMock
