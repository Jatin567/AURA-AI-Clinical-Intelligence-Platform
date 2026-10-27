from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import List, AsyncGenerator
from sse_starlette.sse import EventSourceResponse

from app.patients.models import Session
from app.api.dependencies import get_auth_session, conversation_service, orchestrator_service
from app.conversations.models import Conversation, Message

router = APIRouter(prefix="/chat", tags=["chat"])

class CreateConversationRequest(BaseModel):
    title: str = "New Conversation"
    # Patient context is inferred from the session for now

class RenameRequest(BaseModel):
    title: str

class ChatMessageRequest(BaseModel):
    content: str
    patient_id: str

@router.post("/conversations", response_model=Conversation)
async def create_conversation(req: CreateConversationRequest, session: Session = Depends(get_auth_session)):
    # Fallback to a default patient_id for simplicity, in reality we should look up the active patient profile
    # For now, let's assume we use the user_id as patient_id or allow it to be passed
    # Wait, the user wants Patient Management, but we will use "default_patient" if none is specified.
    # To keep things simple, we'll just use the user_id.
    patient_id = session.user_id 
    conv = conversation_service.create_conversation(patient_id, req.title)
    return conv

@router.get("/conversations", response_model=List[Conversation])
async def list_conversations(session: Session = Depends(get_auth_session)):
    patient_id = session.user_id
    return conversation_service.list_conversations(patient_id)

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, session: Session = Depends(get_auth_session)):
    if not conversation_service.delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "ok"}

@router.patch("/conversations/{conversation_id}")
async def rename_conversation(conversation_id: str, req: RenameRequest, session: Session = Depends(get_auth_session)):
    if not conversation_service.rename_conversation(conversation_id, req.title):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "ok"}

@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_messages(conversation_id: str, session: Session = Depends(get_auth_session)):
    conv = conversation_service.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv.messages

@router.post("/conversations/{conversation_id}/stream")
async def stream_chat(
    conversation_id: str, 
    req: ChatMessageRequest, 
    request: Request,
    session: Session = Depends(get_auth_session)
):
    """
    Accepts a user message, passes it to the ConversationGateway, and streams the response via SSE.
    """
    conv = conversation_service.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    from app.orchestrator.gateway import conversation_gateway

    async def event_generator() -> AsyncGenerator[dict, None]:
        async for chunk in conversation_gateway.process_chat_stream(
            user_id=session.user_id,
            patient_id=req.patient_id,
            conversation_id=conversation_id,
            message=req.content
        ):
            yield {
                "event": chunk.get("event", "message"),
                "data": chunk.get("data", "")
            }

    return EventSourceResponse(event_generator())
