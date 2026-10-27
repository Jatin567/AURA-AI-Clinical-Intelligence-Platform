from fastapi import Header, Depends, HTTPException, status, Request
from redis.asyncio import Redis

from app.session_manager import get_session, SessionNotFoundError
from app.models.session import SessionState


async def get_redis_client(request: Request) -> Redis:
    """
    FastAPI dependency that provides the shared async Redis client from app state.
    """
    return request.app.state.redis


async def get_current_session(
    x_session_id: str = Header(..., description="The session ID returned on creation"),
    redis: Redis = Depends(get_redis_client)
) -> SessionState:
    """
    FastAPI dependency that injects the current session state.
    
    Args:
        x_session_id (str): Session ID from the X-Session-ID header.
        redis (Redis): Injected Redis client.
        
    Returns:
        SessionState: The validated session state.
        
    Raises:
        HTTPException: 404 if the session ID is missing or invalid.
    """
    try:
        session = await get_session(redis, x_session_id)
        return session
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {x_session_id} not found"
        )
