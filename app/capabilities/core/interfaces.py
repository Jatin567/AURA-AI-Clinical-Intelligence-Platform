from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel

class CapabilityMetadata(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    estimated_latency_ms: int = 100
    requires_llm: bool = False
    requires_retrieval: bool = False
    requires_patient_context: bool = False
    requires_workspace: bool = False
    requires_timeline: bool = False
    version: str = "1.0"

class ICapability(ABC):
    @abstractmethod
    def get_metadata(self) -> CapabilityMetadata:
        pass

    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Strictly typed I/O via schemas."""
        pass
