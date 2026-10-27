import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app
from app.models.session import SessionState, IntakeStage
from app.models.intake import IntakeQuestion
from app.models.output import TriageOutput
from app.models.triage import TriageLevel
from app.dependencies import get_current_session, get_redis_client
from app.db.database import get_db_session

client = TestClient(app)

@pytest.fixture
def mock_session():
    return SessionState(
        session_id="test-session-123",
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        intake_stage=IntakeStage.DEMOGRAPHICS
    )

def test_session_creation():
    """POST /session returns a session ID and expiry."""
    # We use app.dependency_overrides to skip Redis requirement for this specific test
    # Or just mock create_session which is called by the route
    with patch("app.api.routes.create_session", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MagicMock(
            session_id="test-session-123",
            expires_at=datetime.now(timezone.utc)
        )
        
        # Override get_redis_client to return a Mock
        app.dependency_overrides[get_redis_client] = lambda: AsyncMock()
        
        with TestClient(app) as client:
            response = client.post("/api/v1/session")
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test-session-123"
        
        app.dependency_overrides = {}

def test_get_question_new_session(mock_session):
    """GET /session/question returns the first question for a new session."""
    app.dependency_overrides[get_current_session] = lambda: mock_session
    
    with TestClient(app) as client:
        response = client.get("/api/v1/session/question", headers={"X-Session-ID": "test-session-123"})
        assert response.status_code == 200
        data = response.json()
        assert "question_id" in data
        assert data["intake_complete"] is False
    
    app.dependency_overrides = {}

def test_post_answer_invalid_input(mock_session):
    """POST /session/answer returns 422 on validation error."""
    app.dependency_overrides[get_current_session] = lambda: mock_session
    app.dependency_overrides[get_redis_client] = lambda: AsyncMock()
    app.dependency_overrides[get_db_session] = lambda: AsyncMock()
    
    from app.intake_engine import IntakeValidationError
    with patch("app.api.routes.intake_engine.process_answer", side_effect=IntakeValidationError("Invalid age")):
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/session/answer", 
                headers={"X-Session-ID": "test-session-123"},
                json={"answer": "invalid", "question_id": "age"}
            )
            assert response.status_code == 422
            assert "Invalid age" in response.json()["detail"]
    
    app.dependency_overrides = {}

def test_get_result_not_ready(mock_session):
    """GET /session/result returns 404 if triage not complete."""
    mock_session.triage_result = None
    app.dependency_overrides[get_current_session] = lambda: mock_session
    
    with TestClient(app) as client:
        response = client.get("/api/v1/session/result", headers={"X-Session-ID": "test-session-123"})
        assert response.status_code == 404
    
    app.dependency_overrides = {}

def test_full_happy_path_triage_flow(mock_session):
    """Verify full flow from answer causing completion to result retrieval."""
    app.dependency_overrides[get_current_session] = lambda: mock_session
    app.dependency_overrides[get_redis_client] = lambda: AsyncMock()
    app.dependency_overrides[get_db_session] = lambda: AsyncMock()
    
    mock_output = TriageOutput(
        session_id="test-session-123",
        triage_level=TriageLevel.ROUTINE,
        triage_label="Schedule Appointment",
        explanation="Test explanation",
        approved_otc_suggestions=[],
        otc_disclaimers=[],
        action_items=[],
        crisis_resources=[],
        medical_disclaimer="Disclaimer",
        assembled_at=datetime.now(timezone.utc),
        llm_was_used=True
    )
    
    with patch("app.api.routes.intake_engine.process_answer"), \
         patch("app.api.routes.intake_engine.is_intake_complete", return_value=True), \
         patch("app.api.routes.red_flag_detector.evaluate"), \
         patch("app.api.routes.severity_classifier.classify"), \
         patch("app.api.routes.llm_orchestrator.generate_explanation", new_callable=AsyncMock), \
         patch("app.api.routes.otc_suggester.validate"), \
         patch("app.api.routes.triage_output_builder.build", return_value=mock_output), \
         patch("app.api.routes.update_session", new_callable=AsyncMock):
        
        with TestClient(app) as client:
            # 1. Post final answer
            response = client.post(
                "/api/v1/session/answer", 
                headers={"X-Session-ID": "test-session-123"},
                json={"answer": "none", "question_id": "history"}
            )
            assert response.status_code == 200
            assert response.json()["intake_complete"] is True
            
            # Simulate result saved
            mock_session.triage_result = mock_output.model_dump()
            
            # 2. Get Result
            response = client.get("/api/v1/session/result", headers={"X-Session-ID": "test-session-123"})
            assert response.status_code == 200
            assert response.json()["triage_label"] == "Schedule Appointment"
    
def test_pipeline_failure_persistence(mock_session):
    """Verify that a pipeline failure persists an error state and returns 503."""
    app.dependency_overrides[get_current_session] = lambda: mock_session
    app.dependency_overrides[get_redis_client] = lambda: AsyncMock()
    app.dependency_overrides[get_db_session] = lambda: AsyncMock()
    
    with patch("app.api.routes.intake_engine.process_answer"), \
         patch("app.api.routes.intake_engine.is_intake_complete", return_value=True), \
         patch("app.api.routes.red_flag_detector.evaluate", side_effect=Exception("Pipeline Crash")), \
         patch("app.api.routes.update_session", new_callable=AsyncMock) as mock_update:
        
        with TestClient(app) as client:
            # 1. Answer triggers pipeline which fails
            response = client.post(
                "/api/v1/session/answer", 
                headers={"X-Session-ID": "test-session-123"},
                json={"answer": "none"}
            )
            assert response.status_code == 200
            
            # Verify error was persisted
            # Call 0: answer update, Call 1: error result update
            assert mock_update.call_count == 2
            error_update = mock_update.call_args_list[1][0][2] # dict arg
            assert "error" in error_update["triage_result"]
            
            # Simulate result saved
            mock_session.triage_result = error_update["triage_result"]
            
            # 2. Get Result returns 503
            response = client.get("/api/v1/session/result", headers={"X-Session-ID": "test-session-123"})
            assert response.status_code == 503
            assert "Triage pipeline failed" in response.json()["detail"]
    
    app.dependency_overrides = {}
