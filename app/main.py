import os
import asyncio
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

# Redis configuration from environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

class FakeRedis:
    """
    In-memory Redis replacement for local development when a real Redis
    instance is not available. Supports get / setex / delete with TTL.
    """
    def __init__(self):
        self._store: dict[str, tuple[str, float]] = {}  # key -> (value, expire_at)

    async def ping(self):
        return True

    async def setex(self, key: str, seconds: int, value: str):
        self._store[key] = (value, time.time() + seconds)

    async def get(self, key: str):
        entry = self._store.get(key)
        if entry is None:
            return None
        value, exp = entry
        if time.time() > exp:
            del self._store[key]
            return None
        return value

    async def delete(self, key: str):
        self._store.pop(key, None)

    async def close(self):
        pass

    async def aclose(self):
        pass


async def _try_connect_redis(url: str):
    """Returns a real Redis client if reachable, otherwise FakeRedis."""
    client = Redis.from_url(url, decode_responses=True, socket_connect_timeout=1)
    try:
        await asyncio.wait_for(client.ping(), timeout=1.0)
        print("INFO:     Connected to Redis at", url)
        return client
    except Exception:
        await client.aclose()
        print("WARNING:  Redis not reachable — using in-memory session store (dev mode)")
        return FakeRedis()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup global redis pool
    global redis_client
    redis_client = await _try_connect_redis(REDIS_URL)
    app.state.redis = redis_client
    yield
    # Cleanup
    pass

app = FastAPI(title="AURA API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.chat_routes import router as chat_router
from app.api.routes import router as session_router
from app.api.patient_routes import router as patient_router
from app.api.workspace_routes import router as workspace_router
from app.api.file_routes import router as file_router
from app.api.speech_routes import router as speech_router
from app.api.knowledge_routes import router as knowledge_router
from app.api.export_routes import router as export_router
from app.api.timeline_routes import router as timeline_router
from app.api.diagnostics_routes import router as diagnostics_router

app.include_router(chat_router, prefix="/api")
app.include_router(session_router, prefix="/api/v1")
app.include_router(patient_router, prefix="/api")
app.include_router(workspace_router, prefix="/api")
app.include_router(file_router, prefix="/api")
app.include_router(speech_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(timeline_router, prefix="/api")
app.include_router(diagnostics_router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
