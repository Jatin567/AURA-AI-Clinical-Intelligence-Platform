import pytest
import pytest_asyncio
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, inspect, text, event
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.db.models import Base, TriageSession, TriageAuditLog

# Use SQLite in-memory for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Enable FK constraints for SQLite
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(db_engine):
    async_session = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.mark.asyncio
async def test_create_triage_session(db_session):
    """Verify TriageSession row creation and UTC defaults."""
    session_id = uuid.uuid4()
    new_session = TriageSession(
        id=session_id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
        intake_stage="demographics",
        had_emergency=False,
        had_crisis_flag=True
    )
    db_session.add(new_session)
    await db_session.commit()

    # Retrieve and verify
    result = await db_session.execute(select(TriageSession).where(TriageSession.id == session_id))
    session = result.scalar_one()
    
    assert session.id == session_id
    assert session.intake_stage == "demographics"
    assert session.had_crisis_flag is True
    assert session.created_at.tzinfo == timezone.utc

@pytest.mark.asyncio
async def test_create_audit_log(db_session):
    """Verify TriageAuditLog linked to a session."""
    session_id = uuid.uuid4()
    session = TriageSession(
        id=session_id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
        intake_stage="complete"
    )
    db_session.add(session)
    
    log = TriageAuditLog(
        session_id=session_id,
        event_type="output_built",
        event_data={"key": "value"},
        classification_version="1.0.0"
    )
    db_session.add(log)
    await db_session.commit()

    # Verify relationship with eager loading
    result = await db_session.execute(
        select(TriageSession).options(selectinload(TriageSession.audit_logs)).where(TriageSession.id == session_id)
    )
    retrieved_session = result.scalar_one()
    assert len(retrieved_session.audit_logs) == 1
    assert retrieved_session.audit_logs[0].event_type == "output_built"
    assert retrieved_session.audit_logs[0].event_data == {"key": "value"}

@pytest.mark.asyncio
async def test_fk_constraint_enforcement(db_session):
    """Verify that audit log without valid session fails."""
    invalid_session_id = uuid.uuid4()
    log = TriageAuditLog(
        session_id=invalid_session_id,
        event_type="test_event",
        event_data={}
    )
    db_session.add(log)
    
    # Note: SQLite requires 'PRAGMA foreign_keys = ON' to be explicitly enabled
    # but SQLAlchemy metadata creation usually handles basic constraints.
    # In async SQLite, we might need a listener or explicit command.
    # However, IntegrityError should be raised on commit if enabled.
    with pytest.raises(IntegrityError):
        await db_session.commit()

@pytest.mark.asyncio
async def test_index_existence(db_engine):
    """Verify that expected indexes are created."""
    async with db_engine.connect() as conn:
        # inspect is synchronous, run_sync is needed
        def get_indexes(connection):
            from sqlalchemy import inspect
            inspector = inspect(connection)
            return {
                "triage_sessions": inspector.get_indexes("triage_sessions"),
                "triage_audit_logs": inspector.get_indexes("triage_audit_logs")
            }
        
        indexes = await conn.run_sync(get_indexes)
        
        # Check TriageSession index
        session_indexes = [idx["name"] for idx in indexes["triage_sessions"]]
        assert "ix_triage_sessions_created_at" in session_indexes
        
        # Check TriageAuditLog indexes
        log_indexes = [idx["name"] for idx in indexes["triage_audit_logs"]]
        assert "ix_triage_audit_logs_session_id" in log_indexes
        assert "ix_triage_audit_logs_event_type" in log_indexes
