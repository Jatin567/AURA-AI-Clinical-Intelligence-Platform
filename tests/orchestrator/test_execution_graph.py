import pytest
from app.orchestrator.execution_graph import ExecutionGraph
from app.orchestrator.ai_session import AISession

def test_execution_graph():
    graph = ExecutionGraph()
    state_tracker = []

    def mock_node(session: AISession):
        state_tracker.append("NODE_EXECUTED")

    graph.add_node("test", mock_node)
    
    session = AISession(session_id="s1", user_id="u1", conversation_id="c1")
    graph.execute(session)
    
    assert "NODE_EXECUTED" in state_tracker
    assert session.state == "COMPLETED"
