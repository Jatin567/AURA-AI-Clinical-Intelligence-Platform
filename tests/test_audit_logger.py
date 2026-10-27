import json
import pytest
import pytest_asyncio
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.audit_logger import (
    log_triage_classification,
    log_otc_evaluation,
    log_output_assembled,
    log_session_error
)
from app.db.models import Base, TriageAuditLog, TriageSession
from app.models.triage import TriageDecision, TriageLevel
from app.models.red_flag import RedFlagResult
from app.models.otc import OTCResult, OTCSuggestion, OTCMedicine
from app.models.output import TriageOutput

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(db_engine):
    async_session = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # Create a session row first to satisfy FK
        session_id = uuid.uuid4()
        db_sess = TriageSession(
            id=session_id,
            expires_at=datetime.now(timezone.utc),
            intake_stage="complete"
        )
        session.add(db_sess)
        await session.commit()
        yield session, str(session_id)

@pytest.mark.asyncio
async def test_log_triage_classification(db_session):
    session, session_id = db_session
    red_flag_res = RedFlagResult(
        session_id=session_id, 
        flags_matched=[],
        evaluated_at=datetime.now(timezone.utc),
        input_snapshot={}
    )
    decision = TriageDecision(
        session_id=session_id,
        triage_level=TriageLevel.URGENT,
        confidence="high",
        primary_reason="Severe pain",
        contributing_factors=["fever"],
        red_flag_result=red_flag_res,
        classified_at=datetime.now(timezone.utc),
        classification_version="1.0"
    )
    
    await log_triage_classification(session_id, decision, session)
    
    result = await session.execute(select(TriageAuditLog).where(TriageAuditLog.event_type == "triage_classified"))
    entry = result.scalar_one()
    assert entry.session_id == uuid.UUID(session_id)
    assert entry.event_data["triage_level"] == "URGENT"
    assert entry.classification_version == "1.0"

@pytest.mark.asyncio
async def test_log_otc_evaluation(db_session):
    session, session_id = db_session
    medicine = OTCMedicine(
        name="Tylenol",
        common_names=[],
        safe_for_ages_above=2,
        contraindicated_conditions=[],
        contraindicated_medications=[],
        max_duration_days=3,
        standard_disclaimer=""
    )
    otc_result = OTCResult(
        session_id=session_id,
        suggestions=[
            OTCSuggestion(medicine=medicine, approved=True),
            OTCSuggestion(medicine=medicine, approved=False, rejection_reason="Age")
        ],
        evaluated_at=datetime.now(timezone.utc),
        triage_level_at_evaluation=TriageLevel.ROUTINE
    )
    
    await log_otc_evaluation(session_id, otc_result, session)
    
    result = await session.execute(select(TriageAuditLog).where(TriageAuditLog.event_type == "otc_evaluated"))
    entry = result.scalar_one()
    assert len(entry.event_data["suggestions"]) == 2
    assert entry.event_data["suggestions"][0]["name"] == "Tylenol"
    assert entry.event_data["suggestions"][1]["rejection_reason"] == "Age"

@pytest.mark.asyncio
async def test_log_output_assembled_scrubbing(db_session):
    session, session_id = db_session
    output = TriageOutput(
        session_id=session_id,
        triage_level=TriageLevel.ROUTINE,
        triage_label="Routine Care",
        explanation="PRIVATE SYMPTOMS: User has a bad headache...", # Should be scrubbed
        approved_otc_suggestions=["Tylenol"],
        otc_disclaimers=[],
        action_items=[],
        crisis_resources=["Help Line"],
        medical_disclaimer="",
        assembled_at=datetime.now(timezone.utc),
        llm_was_used=True
    )
    
    await log_output_assembled(session_id, output, session)
    
    result = await session.execute(select(TriageAuditLog).where(TriageAuditLog.event_type == "output_built"))
    entry = result.scalar_one()
    assert "explanation" not in entry.event_data
    assert "PRIVATE SYMPTOMS" not in str(entry.event_data)
    assert entry.event_data["had_crisis_resource"] is True
    assert entry.event_data["otc_count"] == 1

@pytest.mark.asyncio
async def test_log_session_error(db_session):
    session, session_id = db_session
    await log_session_error(session_id, "PipelineError", "Something crashed", session)
    
    result = await session.execute(select(TriageAuditLog).where(TriageAuditLog.event_type == "error"))
    entry = result.scalar_one()
    assert entry.event_data["error_type"] == "PipelineError"
    assert entry.event_data["error_message"] == "Something crashed"

@pytest.mark.asyncio
async def test_audit_logger_swallows_exceptions(db_session):
    session, session_id = db_session
    # Mock session to raise on commit
    session.commit = AsyncMock(side_effect=Exception("DB DOWN"))
    
    # Should not raise
    await log_session_error(session_id, "type", "msg", session)

@pytest.mark.asyncio
async def test_log_red_flag_scrubbing(db_session):
    """Verify matched_on and input_snapshot are excluded from logs."""
    from app.audit_logger import log_red_flag_evaluation, logger
    from app.models.red_flag import RedFlagMatch, RedFlagSeverity
    
    session, session_id = db_session
    match = RedFlagMatch(
        rule_id="R1",
        severity=RedFlagSeverity.EMERGENCY,
        matched_on="I want to die", # PHI
        explanation="Emergency help needed",
        rule_description="Self harm",
        requires_immediate_crisis_resource=True
    )
    result = RedFlagResult(
        session_id=session_id,
        flags_matched=[match],
        highest_severity=RedFlagSeverity.EMERGENCY,
        evaluated_at=datetime.now(timezone.utc),
        input_snapshot={"text": "I want to die"} # PHI
    )
    
    with patch.object(logger, 'info') as mock_info:
        await log_red_flag_evaluation(session_id, result)
        
        args, _ = mock_info.call_args
        logged_record = json.loads(args[0])
        
        # Verify PHI fields are absent
        assert "input_snapshot" not in logged_record
        for m in logged_record["flags_matched"]:
            assert "matched_on" not in m
            assert "severity" in m
