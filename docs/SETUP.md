# Setup Guide

## Prerequisites

Install:

- Python 3.11 or newer
- Node.js 20 or newer
- npm
- PostgreSQL, optional for local development
- Redis, optional for local development

The backend can run without Redis because `app/main.py` falls back to an in-memory session store when Redis is unavailable.

## Environment Variables

Copy the example environment file:

```powershell
copy .env.example .env
```

Important variables:

```text
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=your-api-key-here
LLM_TIMEOUT_SECONDS=30
LLM_MAX_TOKENS=800
OLLAMA_BASE_URL=http://localhost:11434
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/aura
```

For local demos without cloud LLM calls, use `LLM_PROVIDER=ollama` with a local Ollama model, or keep the provider configured and rely on fallback behavior when the LLM is unavailable.

## Backend Setup

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn redis sqlalchemy asyncpg pydantic-settings httpx pytest pytest-asyncio
```

Run the backend:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Verify:

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8000/health -UseBasicParsing
```

Expected response:

```json
{"status":"healthy"}
```

## Frontend Setup

From the frontend folder:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The Vite config proxies `/api/v1` to `http://localhost:8000`.

## Database Setup

Set `DATABASE_URL` to a PostgreSQL database.

Apply migrations with Alembic after Alembic configuration is completed for the local environment:

```powershell
alembic upgrade head
```

Current migration creates:

- `triage_sessions`
- `triage_audit_logs`

## Running Tests

```powershell
pytest
```

Focused examples:

```powershell
pytest tests/test_reasoning_engine.py
pytest tests/test_adaptive_interview_engine.py
pytest tests/test_safety_fixes.py
```

## Known Setup Gaps

The repository should add a pinned backend dependency file before v1.0:

- `requirements.txt`, or
- `pyproject.toml`

This will make local setup and deployment reproducible.

