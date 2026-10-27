import logging
from typing import Dict, Any
from app.orchestrator.ai_session import AISession

logger = logging.getLogger(__name__)

class ConversationGateway:
    """Entry point handling Authentication, Rate Limiting, Validation, and Session Lookup."""
    
    def __init__(self):
        self.active_sessions: Dict[str, AISession] = {}

    def handle_request(self, user_id: str, conversation_id: str, payload: Dict[str, Any]) -> AISession:
        # Stub Auth and Rate Limiting
        logger.info(f"Gateway authenticating user {user_id}")
        
        # Session Lookup or Create
        session_id = f"{user_id}_{conversation_id}"
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = AISession(
                session_id=session_id,
                user_id=user_id,
                conversation_id=conversation_id
            )
        
        session = self.active_sessions[session_id]
        session.transition_state("COLLECTING_INFORMATION")
        return session

    async def process_chat_stream(self, user_id: str, patient_id: str, conversation_id: str, message: str):
        from app.api.dependencies import conversation_service, orchestrator_service
        import json
        
        from app.api.dependencies import event_bus

        conv = conversation_service.get_conversation(conversation_id)
        if not conv:
            conv = conversation_service.create_conversation(patient_id, title="New Conversation")
            conversation_id = conv.conversation_id
            event_bus.publish("ConversationStarted", {"conversation_id": conversation_id, "patient_id": patient_id})
            
        conversation_service.add_message(conversation_id, "user", message)
        
        session = self.handle_request(user_id, conversation_id, {"msg": message})
        
        yield {"event": "STATUS", "data": json.dumps({"status": "generating"})}
        yield {"event": "HEARTBEAT", "data": json.dumps({"status": "alive"})}

        assembled = ""
        persisted = False
        try:
            async for chunk in orchestrator_service.handle_message_async_stream(user_id, conversation_id, {"msg": message}):
                event = chunk.get("event")
                if event == "TEXT_CHUNK":
                    try:
                        data = json.loads(chunk["data"])
                        assembled += data.get("text") or ""
                    except Exception:
                        pass
                elif event == "COMPLETE":
                    full_response_text = assembled
                    try:
                        data = json.loads(chunk["data"])
                        if data.get("full_response"):
                            full_response_text = data["full_response"]
                    except Exception:
                        pass
                    if full_response_text.strip():
                        conversation_service.add_message(conversation_id, "assistant", full_response_text)
                        event_bus.publish("ConversationCompleted", {"conversation_id": conversation_id, "patient_id": patient_id})
                        persisted = True
                elif event == "ERROR":
                    try:
                        data = json.loads(chunk["data"])
                        err_text = data.get("message") or "I could not generate a reply just then."
                    except Exception:
                        err_text = "I could not generate a reply just then."
                    if not assembled.strip():
                        conversation_service.add_message(conversation_id, "assistant", err_text)
                        persisted = True
                yield chunk
        finally:
            if not persisted and assembled.strip():
                conversation_service.add_message(conversation_id, "assistant", assembled)
                event_bus.publish("ConversationCompleted", {"conversation_id": conversation_id, "patient_id": patient_id})
            
conversation_gateway = ConversationGateway()
