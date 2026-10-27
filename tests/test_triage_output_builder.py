import pytest
from datetime import datetime, timezone, timedelta
from app.models.session import SessionState, PatientProfile
from app.models.triage import TriageLevel, TriageDecision
from app.models.red_flag import RedFlagResult, RedFlagMatch
from app.models.llm import OrchestratorResult, LLMResponse
from app.models.otc import OTCResult, OTCSuggestion, OTCMedicine
from app.triage_output_builder import TriageOutputBuilder

@pytest.fixture
def builder():
    return TriageOutputBuilder()

@pytest.fixture
def base_session():
    now = datetime.now(timezone.utc)
    return SessionState(
        session_id="test-session-output",
        created_at=now,
        expires_at=now + timedelta(hours=2)
    )

@pytest.fixture
def mock_red_flag_result():
    return RedFlagResult(
        evaluated_at=datetime.now(timezone.utc),
        flags_matched=[],
        highest_severity=None,
        input_snapshot={}
    )

@pytest.fixture
def base_triage_decision(mock_red_flag_result):
    return TriageDecision(
        session_id="test-session-output",
        triage_level=TriageLevel.ROUTINE,
        confidence="high",
        primary_reason="Test reason",
        red_flag_result=mock_red_flag_result,
        classified_at=datetime.now(timezone.utc)
    )

@pytest.fixture
def base_otc_result():
    return OTCResult(
        session_id="test-session-output",
        suggestions=[],
        evaluated_at=datetime.now(timezone.utc),
        triage_level_at_evaluation=TriageLevel.ROUTINE
    )

def test_label_mapping(builder, base_session, base_triage_decision, base_otc_result):
    """Verifies each triage level maps to the correct human-readable label."""
    levels = [
        (TriageLevel.EMERGENCY, "Seek Emergency Care Immediately — Call 911"),
        (TriageLevel.URGENT, "See a Doctor Within 24 Hours"),
        (TriageLevel.ROUTINE, "Schedule a Doctor Appointment"),
        (TriageLevel.HOME_CARE, "You Can Manage This at Home")
    ]
    
    for level, expected_label in levels:
        base_triage_decision.triage_level = level
        orchestrator_result = OrchestratorResult(
            session_id=base_session.session_id,
            triage_decision=base_triage_decision,
            llm_skipped=True,
            assembled_at=datetime.now(timezone.utc)
        )
        
        output = builder.build(base_session, orchestrator_result, base_otc_result)
        assert output.triage_label == expected_label

def test_emergency_static_explanation(builder, base_session, base_triage_decision, base_otc_result):
    """Rule: EMERGENCY triage uses static explanation when LLM is skipped."""
    base_triage_decision.triage_level = TriageLevel.EMERGENCY
    orchestrator_result = OrchestratorResult(
        session_id=base_session.session_id,
        triage_decision=base_triage_decision,
        llm_skipped=True,
        skip_reason="Emergency",
        assembled_at=datetime.now(timezone.utc)
    )
    
    output = builder.build(base_session, orchestrator_result, base_otc_result)
    assert "immediate emergency medical attention" in output.explanation
    assert "Do not drive yourself" in output.explanation

def test_llm_failure_uses_fallback(builder, base_session, base_triage_decision, base_otc_result):
    """Rule: If LLM fails, use static fallback explanation."""
    base_triage_decision.triage_level = TriageLevel.URGENT
    orchestrator_result = OrchestratorResult(
        session_id=base_session.session_id,
        triage_decision=base_triage_decision,
        llm_response=LLMResponse(
            explanation="Failed text",
            suggested_questions=[],
            otc_candidates=[],
            raw_response="",
            model_used="gpt-4",
            generation_error="Timeout Error"
        ),
        assembled_at=datetime.now(timezone.utc)
    )
    
    output = builder.build(base_session, orchestrator_result, base_otc_result)
    assert "prompt medical evaluation" in output.explanation  # Static URGENT fallback

def test_crisis_resource_injection(builder, base_session, base_triage_decision, base_otc_result):
    """Rule: Inject crisis resource if flag is set, regardless of everything else."""
    base_triage_decision.red_flag_result.flags_matched = [
        RedFlagMatch(
            rule_id="mental_health_crisis",
            rule_description="Check for mental health crisis",
            matched_on="suicide",
            explanation="Suicidal ideation",
            severity="EMERGENCY",
            requires_immediate_crisis_resource=True
        )
    ]
    
    orchestrator_result = OrchestratorResult(
        session_id=base_session.session_id,
        triage_decision=base_triage_decision,
        llm_skipped=True,
        assembled_at=datetime.now(timezone.utc)
    )
    
    output = builder.build(base_session, orchestrator_result, base_otc_result)
    assert len(output.crisis_resources) == 1
    assert "988" in output.crisis_resources[0]

def test_no_crisis_resource_when_not_flagged(builder, base_session, base_triage_decision, base_otc_result):
    """Rule: No crisis resource when flag is False."""
    base_triage_decision.red_flag_result.flags_matched = [
        RedFlagMatch(
            rule_id="fever",
            rule_description="Check for high fever",
            matched_on="fever",
            explanation="High fever",
            severity="URGENT",
            requires_immediate_crisis_resource=False
        )
    ]
    
    orchestrator_result = OrchestratorResult(
        session_id=base_session.session_id,
        triage_decision=base_triage_decision,
        llm_skipped=True,
        assembled_at=datetime.now(timezone.utc)
    )
    
    output = builder.build(base_session, orchestrator_result, base_otc_result)
    assert output.crisis_resources == []

def test_otc_formatting(builder, base_session, base_triage_decision, base_otc_result):
    """Rule: Approved OTCs are formatted correctly, rejected ones are omitted."""
    medicine = OTCMedicine(
        name="Ibuprofen",
        common_names=["Advil", "Motrin"],
        safe_for_ages_above=12,
        contraindicated_conditions=[],
        contraindicated_medications=[],
        max_duration_days=10,
        standard_disclaimer="Take with food."
    )
    
    base_otc_result.suggestions = [
        OTCSuggestion(medicine=medicine, approved=True),
        OTCSuggestion(
            medicine=OTCMedicine(
                name="Aspirin",
                common_names=[],
                safe_for_ages_above=0,
                contraindicated_conditions=[],
                contraindicated_medications=[],
                max_duration_days=0,
                standard_disclaimer=""
            ),
            approved=False,
            rejection_reason="Not in allowlist"
        )
    ]
    
    orchestrator_result = OrchestratorResult(
        session_id=base_session.session_id,
        triage_decision=base_triage_decision,
        llm_skipped=False,
        llm_response=LLMResponse(
            explanation="Normal explanation",
            suggested_questions=[],
            otc_candidates=[],
            raw_response="",
            model_used="gpt-4"
        ),
        assembled_at=datetime.now(timezone.utc)
    )
    
    output = builder.build(base_session, orchestrator_result, base_otc_result)
    assert len(output.approved_otc_suggestions) == 1
    assert "Ibuprofen (Advil, Motrin) — Take with food." in output.approved_otc_suggestions[0]
    assert "Take with food." in output.otc_disclaimers

def test_action_items_per_level(builder, base_session, base_triage_decision, base_otc_result):
    """Rule: Action items match triage level exactly."""
    levels = [
        (TriageLevel.EMERGENCY, "Call 911 immediately"),
        (TriageLevel.URGENT, "Contact your doctor or urgent care today"),
        (TriageLevel.ROUTINE, "Schedule an appointment with your doctor"),
        (TriageLevel.HOME_CARE, "Rest and stay hydrated")
    ]
    
    for level, expected_item in levels:
        base_triage_decision.triage_level = level
        orchestrator_result = OrchestratorResult(
            session_id=base_session.session_id,
            triage_decision=base_triage_decision,
            llm_skipped=True,
            assembled_at=datetime.now(timezone.utc)
        )
        
        output = builder.build(base_session, orchestrator_result, base_otc_result)
        assert expected_item in output.action_items

def test_medical_disclaimer_always_present(builder, base_session, base_triage_decision, base_otc_result):
    """Rule: Universal medical disclaimer is always present."""
    orchestrator_result = OrchestratorResult(
        session_id=base_session.session_id,
        triage_decision=base_triage_decision,
        llm_skipped=True,
        assembled_at=datetime.now(timezone.utc)
    )
    
    output = builder.build(base_session, orchestrator_result, base_otc_result)
    assert "AI-powered triage assistant" in output.medical_disclaimer
    assert "consult a qualified healthcare professional" in output.medical_disclaimer
