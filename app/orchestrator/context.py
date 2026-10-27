from typing import Dict, Any, List
from pydantic import BaseModel
from abc import ABC, abstractmethod

class ContextSnapshot(BaseModel):
    """Immutable state snapshot collected before LLM execution."""
    patient: Dict[str, Any] = {}
    memory: List[Dict[str, Any]] = []
    timeline: Dict[str, Any] = {}
    workspace: Dict[str, Any] = {}
    assessment: Dict[str, Any] = {}
    uploads: List[Dict[str, Any]] = []

class ContextProvider(ABC):
    @abstractmethod
    def name(self) -> str: pass
    
    @abstractmethod
    async def collect(self, user_id: str, patient_id: str, conversation_id: str) -> Any: pass

class PatientContextProvider(ContextProvider):
    def name(self) -> str: return "patient"
    async def collect(self, user_id: str, patient_id: str, conversation_id: str) -> Dict[str, Any]:
        return {"id": patient_id, "mock_data": True}

class MemoryContextProvider(ContextProvider):
    def name(self) -> str: return "memory"
    async def collect(self, user_id: str, patient_id: str, conversation_id: str) -> List[Dict[str, Any]]:
        return []

class ContextManager:
    def __init__(self):
        self.providers: List[ContextProvider] = [
            PatientContextProvider(),
            MemoryContextProvider()
        ]
        
    async def build_snapshot(self, user_id: str, patient_id: str, conversation_id: str) -> ContextSnapshot:
        snapshot_data = {}
        for p in self.providers:
            snapshot_data[p.name()] = await p.collect(user_id, patient_id, conversation_id)
        return ContextSnapshot(**snapshot_data)

context_manager = ContextManager()
