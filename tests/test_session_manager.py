import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.session_manager import create_session, get_session, update_session, delete_session, SessionNotFoundError
from app.models.session import SessionState, IntakeStage

@pytest.fixture
def mock_redis():
    """Provides a mocked async Redis client."""
    redis = AsyncMock()
    # Mock storage dictionary to simulate Redis behavior
    storage = {}

    async def mock_setex(key, ttl, value):
        storage[key] = value
        return True

    async def mock_get(key):
        return storage.get(key)

    async def mock_expire(key, ttl):
        return key in storage

    async def mock_delete(key):
        if key in storage:
            del storage[key]
            return 1
        return 0

    redis.setex.side_effect = mock_setex
    redis.get.side_effect = mock_get
    redis.expire.side_effect = mock_expire
    redis.delete.side_effect = mock_delete
    return redis


@pytest.mark.asyncio
async def test_create_session(mock_redis):
    """Verifies that a session can be created and stored."""
    state = await create_session(mock_redis)
    
    assert state.session_id is not None
    assert state.expires_at is not None
    assert state.expires_at > state.created_at
    assert state.intake_stage == IntakeStage.DEMOGRAPHICS
    
    # Verify setex was called with correct key and data
    mock_redis.setex.assert_called_once()
    args = mock_redis.setex.call_args[0]
    assert args[0] == f"session:{state.session_id}"
    assert args[1] == 7200


@pytest.mark.asyncio
async def test_get_session_success(mock_redis):
    """Verifies retrieval of an existing session and expiry refresh."""
    # First create a session
    original_state = await create_session(mock_redis)
    session_id = original_state.session_id
    original_expiry = original_state.expires_at
    
    # Reset mock to clean call history
    mock_redis.setex.reset_mock()
    
    # Retrieve it
    retrieved_state = await get_session(mock_redis, session_id)
    
    assert retrieved_state.session_id == session_id
    assert retrieved_state.expires_at > original_expiry
    
    mock_redis.get.assert_called_with(f"session:{session_id}")
    # Verify it was saved back with new TTL
    mock_redis.setex.assert_called()


@pytest.mark.asyncio
async def test_get_session_not_found(mock_redis):
    """Verifies that SessionNotFoundError is raised for missing sessions."""
    with pytest.raises(SessionNotFoundError):
        await get_session(mock_redis, "non-existent-id")


@pytest.mark.asyncio
async def test_update_session(mock_redis):
    """Verifies that session state can be updated."""
    state = await create_session(mock_redis)
    session_id = state.session_id
    
    updates = {
        "intake_stage": "symptoms",
        "patient_profile": {"age": 30, "sex": "male"}
    }
    
    updated_state = await update_session(mock_redis, session_id, updates)
    
    assert updated_state.intake_stage == IntakeStage.SYMPTOMS
    assert updated_state.patient_profile.age == 30
    assert updated_state.patient_profile.sex == "male"
    assert updated_state.last_modified_at is not None
    
    # Verify it was saved back to Redis
    mock_redis.setex.assert_called()


@pytest.mark.asyncio
async def test_delete_session(mock_redis):
    """Verifies that a session can be deleted."""
    state = await create_session(mock_redis)
    session_id = state.session_id
    
    await delete_session(mock_redis, session_id)
    mock_redis.delete.assert_called_with(f"session:{session_id}")
    
    # Subsequent get should fail
    with pytest.raises(SessionNotFoundError):
        await get_session(mock_redis, session_id)
@pytest.mark.asyncio
async def test_update_session_deep_merge(mock_redis):
    """Verifies that nested objects are merged recursively, not overwritten."""
    # 1. Create session with some initial data
    state = await create_session(mock_redis)
    session_id = state.session_id
    
    initial_updates = {
        "patient_profile": {
            "age": 25,
            "allergies": ["peanuts"]
        }
    }
    await update_session(mock_redis, session_id, initial_updates)
    
    # 2. Update ONLY age in patient_profile
    partial_update = {
        "patient_profile": {
            "age": 34
        }
    }
    updated_state = await update_session(mock_redis, session_id, partial_update)
    
    # 3. Assertions
    assert updated_state.patient_profile.age == 34
    # Ensure allergies were NOT wiped out
    assert "peanuts" in updated_state.patient_profile.allergies
    assert updated_state.patient_profile.allergies == ["peanuts"]


@pytest.mark.asyncio
async def test_update_session_history_cap(mock_redis):
    """Verifies that conversation_history is trimmed to the last 100 entries."""
    state = await create_session(mock_redis)
    session_id = state.session_id
    
    # Create 110 entries
    large_history = [{"msg": f"message {i}"} for i in range(110)]
    updates = {"conversation_history": large_history}
    
    updated_state = await update_session(mock_redis, session_id, updates)
    
    # Assertions
    assert len(updated_state.conversation_history) == 100
    # Should keep the LAST 100 (from 10 to 109)
    assert updated_state.conversation_history[0]["msg"] == "message 10"
    assert updated_state.conversation_history[-1]["msg"] == "message 109"
