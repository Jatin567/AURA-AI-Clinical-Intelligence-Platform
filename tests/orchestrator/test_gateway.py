import pytest
from app.orchestrator.gateway import ConversationGateway

def test_gateway_handle_request():
    gateway = ConversationGateway()
    session = gateway.handle_request("u1", "c1", {"msg": "hi"})
    assert session.session_id == "u1_c1"
    assert session.state == "COLLECTING_INFORMATION"
