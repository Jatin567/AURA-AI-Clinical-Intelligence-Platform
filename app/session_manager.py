import json
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from typing import Optional
from redis.asyncio import Redis

from app.models.session import SessionState


class SessionNotFoundError(Exception):
    """Raised when a session is not found in Redis."""
    pass


async def create_session(redis: Redis) -> SessionState:
    """
    Creates a new session, saves it to Redis with a 2-hour TTL, and returns the state.
    
    Args:
        redis (Redis): The async Redis client.
        
    Returns:
        SessionState: The newly created session state.
    """
    session_id = str(uuid4())
    now = datetime.now(timezone.utc)
    state = SessionState(
        session_id=session_id,
        created_at=now,
        expires_at=now + timedelta(hours=2)
    )
    
    await redis.setex(
        f"session:{session_id}",
        7200,  # 2 hours in seconds
        state.model_dump_json()
    )
    return state


async def get_session(redis: Redis, session_id: str) -> Optional[SessionState]:
    """
    Retrieves a session from Redis and resets its TTL.
    
    Args:
        redis (Redis): The async Redis client.
        session_id (str): The session identifier.
        
    Returns:
        Optional[SessionState]: The session state if found, else None.
        
    Raises:
        SessionNotFoundError: If the session does not exist.
    """
    data = await redis.get(f"session:{session_id}")
    if not data:
        raise SessionNotFoundError(f"Session {session_id} not found")
    
    state = SessionState.model_validate_json(data)
    
    # Refresh expires_at and save back to Redis to keep JSON in sync with TTL
    now = datetime.now(timezone.utc)
    state.expires_at = now + timedelta(hours=2)
    
    await redis.setex(
        f"session:{session_id}",
        7200,
        state.model_dump_json()
    )
    
    return state


async def update_session(redis: Redis, session_id: str, updates: dict) -> SessionState:
    """
    Updates an existing session with new data and resets its TTL.
    
    Args:
        redis (Redis): The async Redis client.
        session_id (str): The session identifier.
        updates (dict): A dictionary of fields to update.
        
    Returns:
        SessionState: The updated session state.
    
    Raises:
        SessionNotFoundError: If the session does not exist.
    """
    state = await get_session(redis, session_id)
    
    # Simple update for flat fields or nested model updates if provided as dicts
    # Note: For production, a more robust deep merge might be needed for complex objects.
    # Refresh expires_at and update last_modified_at
    current_data = state.model_dump()
    now = datetime.now(timezone.utc)
    current_data["expires_at"] = now + timedelta(hours=2)
    current_data["last_modified_at"] = now
    
    def deep_update(base_dict, update_dict):
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
        
        # Enforce conversation history cap if it was updated
        if "conversation_history" in update_dict and isinstance(base_dict.get("conversation_history"), list):
            base_dict["conversation_history"] = base_dict["conversation_history"][-100:]
            
        return base_dict

    updated_data = deep_update(current_data, updates)
    new_state = SessionState.model_validate(updated_data)
    
    await redis.setex(
        f"session:{session_id}",
        7200,
        new_state.model_dump_json()
    )
    return new_state


async def delete_session(redis: Redis, session_id: str) -> None:
    """
    Deletes a session from Redis.
    
    Args:
        redis (Redis): The async Redis client.
        session_id (str): The session identifier.
    """
    await redis.delete(f"session:{session_id}")
