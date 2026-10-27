import pytest
from app.orchestrator.ai_session import AISession

def test_ai_session_state():
    session = AISession(session_id="s1", user_id="u1", conversation_id="c1")
    assert session.state == "IDLE"
    session.transition_state("RUNNING")
    assert session.state == "RUNNING"
