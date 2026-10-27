from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    message_id: str
    role: str  # "user", "assistant", "system"
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Conversation(BaseModel):
    conversation_id: str
    patient_id: str
    title: str = "New Conversation"
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
