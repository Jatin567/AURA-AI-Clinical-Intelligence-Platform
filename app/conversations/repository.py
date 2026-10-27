import threading
import json
import os
from typing import List, Optional
from app.conversations.models import Conversation

class ConversationRepository:
    def save_conversation(self, conversation: Conversation) -> None:
        pass
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        pass
    def list_conversations_for_patient(self, patient_id: str) -> List[Conversation]:
        pass
    def delete_conversation(self, conversation_id: str) -> bool:
        pass

class InMemoryConversationRepository(ConversationRepository):
    """
    In-memory storage for conversations.
    """
    def __init__(self):
        self._conversations = {}  # conversation_id -> Conversation
        self._lock = threading.Lock()

    def save_conversation(self, conversation: Conversation) -> None:
        with self._lock:
            self._conversations[conversation.conversation_id] = conversation

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        with self._lock:
            return self._conversations.get(conversation_id)

    def list_conversations_for_patient(self, patient_id: str) -> List[Conversation]:
        with self._lock:
            return sorted(
                [c for c in self._conversations.values() if c.patient_id == patient_id],
                key=lambda x: x.updated_at,
                reverse=True
            )

    def delete_conversation(self, conversation_id: str) -> bool:
        with self._lock:
            if conversation_id in self._conversations:
                del self._conversations[conversation_id]
                return True
            return False

class FileBasedConversationRepository(ConversationRepository):
    """File-based persistent storage for conversations."""
    def __init__(self, directory: str = "app/data/conversations"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self._lock = threading.Lock()
        # In-memory cache to prevent 404s from file I/O race conditions
        self._cache: dict = {}

    def _get_path(self, conversation_id: str) -> str:
        return os.path.join(self.directory, f"{conversation_id}.json")

    def save_conversation(self, conversation: Conversation) -> None:
        with self._lock:
            self._cache[conversation.conversation_id] = conversation
            with open(self._get_path(conversation.conversation_id), "w") as f:
                f.write(conversation.model_dump_json())

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        with self._lock:
            # Check cache first — avoids file I/O race conditions
            if conversation_id in self._cache:
                return self._cache[conversation_id]
            path = self._get_path(conversation_id)
            if not os.path.exists(path):
                return None
            try:
                with open(path, "r", encoding="utf-8") as f:
                    conv = Conversation.model_validate_json(f.read())
                    self._cache[conversation_id] = conv
                    return conv
            except Exception:
                return None

    def list_conversations_for_patient(self, patient_id: str) -> List[Conversation]:
        with self._lock:
            conversations = []
            for filename in os.listdir(self.directory):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(self.directory, filename), "r") as f:
                            conv = Conversation.model_validate_json(f.read())
                            if conv.patient_id == patient_id:
                                conversations.append(conv)
                    except Exception:
                        pass
            return sorted(conversations, key=lambda x: x.updated_at, reverse=True)

    def delete_conversation(self, conversation_id: str) -> bool:
        with self._lock:
            self._cache.pop(conversation_id, None)
            path = self._get_path(conversation_id)
            if os.path.exists(path):
                os.remove(path)
                return True
            return False
