import uuid
from datetime import datetime, timezone
from typing import List, Optional

from app.conversations.models import Conversation, Message
from app.conversations.repository import InMemoryConversationRepository

class ConversationService:
    def __init__(self, repo: InMemoryConversationRepository):
        self.repo = repo

    def create_conversation(self, patient_id: str, title: str = "New Conversation") -> Conversation:
        conversation = Conversation(
            conversation_id=str(uuid.uuid4()),
            patient_id=patient_id,
            title=title
        )
        self.repo.save_conversation(conversation)
        return conversation

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return self.repo.get_conversation(conversation_id)

    def list_conversations(self, patient_id: str) -> List[Conversation]:
        return self.repo.list_conversations_for_patient(patient_id)

    def add_message(self, conversation_id: str, role: str, content: str) -> Optional[Message]:
        conversation = self.repo.get_conversation(conversation_id)
        if not conversation:
            return None

        if conversation.messages:
            last = conversation.messages[-1]
            if last.role == role and last.content.strip() == content.strip():
                return last

        message = Message(
            message_id=str(uuid.uuid4()),
            role=role,
            content=content
        )
        conversation.messages.append(message)
        conversation.updated_at = datetime.now(timezone.utc)
        self.repo.save_conversation(conversation)
        return message

    def rename_conversation(self, conversation_id: str, new_title: str) -> bool:
        conversation = self.repo.get_conversation(conversation_id)
        if not conversation:
            return False
        conversation.title = new_title
        conversation.updated_at = datetime.now(timezone.utc)
        self.repo.save_conversation(conversation)
        return True

    def delete_conversation(self, conversation_id: str) -> bool:
        return self.repo.delete_conversation(conversation_id)
