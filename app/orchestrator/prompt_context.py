from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.orchestrator.memory_selector import MemorySelector
from app.orchestrator.context_prioritizer import ContextPrioritizer
from app.knowledge.retrieval.models import EvidencePackage

class PromptContext(BaseModel):
    patient_profile: Dict[str, Any]
    timeline: List[Dict[str, Any]]
    workspace: List[Dict[str, Any]]
    memory: Dict[str, Any]
    retrieved_evidence: Optional[EvidencePackage] = None
    clinical_recommendations: List[str]
    missing_information: List[str]
    drug_safety: List[str]
    current_message: str

class PromptContextBuilder:
    def __init__(self, memory_selector: MemorySelector, context_prioritizer: ContextPrioritizer):
        self.memory_selector = memory_selector
        self.prioritizer = context_prioritizer

    def build(self, raw_data: Dict[str, Any]) -> PromptContext:
        memory = self.memory_selector.select_memory(raw_data.get("memory", {}))
        
        prioritized_timeline = self.prioritizer.prioritize({"items": raw_data.get("timeline", [])})
        
        return PromptContext(
            patient_profile=raw_data.get("patient_profile", {}),
            timeline=prioritized_timeline,
            workspace=raw_data.get("workspace", []),
            memory=memory,
            retrieved_evidence=raw_data.get("evidence_package"),
            clinical_recommendations=raw_data.get("clinical_recommendations", []),
            missing_information=raw_data.get("missing_information", []),
            drug_safety=raw_data.get("drug_safety", []),
            current_message=raw_data.get("current_message", "")
        )
