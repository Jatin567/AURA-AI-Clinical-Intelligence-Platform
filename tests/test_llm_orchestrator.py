import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from app.models.session import SessionState, PatientProfile
from app.models.triage import TriageDecision, TriageLevel
from app.models.red_flag import RedFlagResult
from app.llm_orchestrator import LLMOrchestrator
from app.config import settings

@pytest.fixture
def orchestrator():
    return LLMOrchestrator()

@pytest.fixture
def base_session():
    now = datetime.now(timezone.utc)
    return SessionState(
        session_id="test-session-llm",
        created_at=now,
        expires_at=now + timedelta(hours=2),
        patient_profile=PatientProfile(age=45, sex="male", known_conditions=["Asthma"]),
        chief_complaint="Shortness of breath",
        symptom_duration="2 hours",
        symptom_severity=8,
        conversation_history=[{"question_id": f"q{i}", "question_text": f"text{i}", "answer": f"ans{i}"} for i in range(15)]
    )

@pytest.fixture
def urgent_triage():
    return TriageDecision(
        session_id="test-session-llm",
        triage_level=TriageLevel.URGENT,
        confidence="medium",
        primary_reason="Severe shortness of breath",
        contributing_factors=["Severity 8"],
        red_flag_result=RedFlagResult(
            evaluated_at=datetime.now(timezone.utc),
            flags_matched=[],
            highest_severity=None,
            input_snapshot={}
        ),
        classified_at=datetime.now(timezone.utc)
    )

@pytest.mark.asyncio
async def test_emergency_skips_llm(orchestrator, base_session):
    """Rule 1: EMERGENCY triage skips LLM entirely."""
    emergency_triage = TriageDecision(
        session_id="test-session-llm",
        triage_level=TriageLevel.EMERGENCY,
        confidence="high",
        primary_reason="Critical red flag",
        red_flag_result=RedFlagResult(
            evaluated_at=datetime.now(timezone.utc),
            flags_matched=[],
            highest_severity=None,
            input_snapshot={}
        ),
        classified_at=datetime.now(timezone.utc)
    )
    
    with patch.object(orchestrator, '_call_llm_api', new_callable=AsyncMock) as mock_call:
        result = await orchestrator.generate_explanation(base_session, emergency_triage)
        
        assert result.llm_skipped is True
        assert "immediate action required" in result.skip_reason
        assert result.llm_response is None
        mock_call.assert_not_called()

@pytest.mark.asyncio
async def test_successful_llm_generation_and_otc_parsing(orchestrator, base_session, urgent_triage):
    """Verifies successful LLM call and parsing of OTC candidates."""
    mock_llm_response = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "Explanation text here.\nOTC_CANDIDATES: Paracetamol, Ibuprofen\nMedical disclaimer at the end."
            }
        }],
        "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        "model": "gpt-4o-mini"
    }
    
    with patch.object(orchestrator, '_call_llm_api', return_value=mock_llm_response):
        result = await orchestrator.generate_explanation(base_session, urgent_triage)
        
        assert result.llm_response.explanation == "Explanation text here.\nMedical disclaimer at the end."
        assert result.llm_response.otc_candidates == ["Paracetamol", "Ibuprofen"]
        assert result.llm_skipped is False
        assert result.llm_response.generation_error is None

@pytest.mark.asyncio
async def test_llm_failure_safe_fallback(orchestrator, base_session, urgent_triage):
    """Verifies that LLM failure returns a safe fallback and records the error."""
    with patch.object(orchestrator, '_call_llm_api', side_effect=Exception("API Connection Failed")):
        result = await orchestrator.generate_explanation(base_session, urgent_triage)
        
        assert "automated detailed explanation" in result.llm_response.explanation.lower()
        assert result.llm_response.generation_error == "API Connection Failed"
        assert result.llm_response.otc_candidates == []

@pytest.mark.asyncio
async def test_llm_timeout_safe_fallback(orchestrator, base_session, urgent_triage):
    """Verifies that LLM timeout returns a safe fallback."""
    # Temporarily shorten timeout for test
    with patch('app.config.settings.LLM_TIMEOUT_SECONDS', 0.1):
        async def slow_call(*args, **kwargs):
            await asyncio.sleep(0.5)
            return {}
            
        with patch.object(orchestrator, '_call_llm_api', side_effect=slow_call):
            result = await orchestrator.generate_explanation(base_session, urgent_triage)
            assert "delay" in result.llm_response.explanation.lower()
            assert "timed out" in result.llm_response.generation_error.lower()

def test_prompt_history_limit(orchestrator, base_session, urgent_triage):
    """Verifies that the prompt includes only the last 10 conversation turns."""
    prompt = orchestrator._construct_user_prompt(base_session, urgent_triage)
    
    # Range was 15, so 0-4 should be missing
    assert "text0" not in prompt
    assert "text4" not in prompt
    assert "text5" in prompt
    assert "text14" in prompt

def test_system_prompt_immutability(orchestrator, urgent_triage):
    """Verifies that the system prompt correctly interpolates the triage level."""
    system_prompt = orchestrator.SYSTEM_PROMPT_TEMPLATE.format(
        triage_level=urgent_triage.triage_level.value,
        primary_reason=urgent_triage.primary_reason
    )
    
    assert "The triage level is URGENT" in system_prompt
    assert "Severe shortness of breath" in system_prompt
    assert "Never diagnose" in system_prompt

@pytest.mark.asyncio
async def test_ollama_success(orchestrator, base_session, urgent_triage):
    """Test successful Ollama call and parsing."""
    mock_ollama_response = {
        "model": "llama3.2",
        "message": {
            "role": "assistant",
            "content": "Explanation text.\nOTC_CANDIDATES: Paracetamol\nMedical disclaimer."
        },
        "done": True,
        "prompt_eval_count": 100,
        "eval_count": 50
    }

    with patch('app.config.settings.LLM_PROVIDER', 'ollama'):
        with patch('app.config.settings.OLLAMA_BASE_URL', 'http://localhost:11434'):
            with patch('httpx.AsyncClient') as mock_client_cls:
                mock_client = AsyncMock()
                mock_client_cls.return_value.__aenter__.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = mock_ollama_response
                mock_response.raise_for_status = MagicMock()
                
                mock_client.post = AsyncMock(return_value=mock_response)

                result = await orchestrator.generate_explanation(base_session, urgent_triage)
                
                assert result.llm_response is not None
                assert result.llm_response.otc_candidates == ["Paracetamol"]
                assert result.llm_response.model_used == "llama3.2"
                assert result.llm_response.prompt_tokens == 100
                assert result.llm_response.completion_tokens == 50
                
                assert result.llm_response is not None
                assert result.llm_response.otc_candidates == ["Paracetamol"]
                assert result.llm_response.model_used == "llama3.2"
                assert result.llm_response.prompt_tokens == 100
                assert result.llm_response.completion_tokens == 50

@pytest.mark.asyncio
async def test_ollama_unavailable_fallback(orchestrator, base_session, urgent_triage):
    """Test fallback when Ollama server is unreachable."""
    with patch('app.config.settings.LLM_PROVIDER', 'ollama'):
        with patch('httpx.AsyncClient.post', side_effect=Exception("Connection refused")):
            result = await orchestrator.generate_explanation(base_session, urgent_triage)
            
            assert "delay" in result.llm_response.explanation.lower()
            assert result.llm_response.generation_error is not None
            assert result.llm_response.otc_candidates == []
