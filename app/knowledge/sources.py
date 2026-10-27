from abc import ABC, abstractmethod
from typing import List, Dict, Any

class KnowledgeSource(ABC):
    @abstractmethod
    def name(self) -> str:
        pass
        
    @abstractmethod
    async def retrieve(self, query: str, context: Dict[str, Any], max_results: int = 5) -> List[Dict[str, Any]]:
        pass

class MedicalGuidelinesSource(KnowledgeSource):
    def name(self) -> str: return "guidelines"
    async def retrieve(self, query: str, context: Dict[str, Any], max_results: int = 5) -> List[Dict[str, Any]]:
        return []

class PatientMemorySource(KnowledgeSource):
    def name(self) -> str: return "memory"
    async def retrieve(self, query: str, context: Dict[str, Any], max_results: int = 5) -> List[Dict[str, Any]]:
        return []
