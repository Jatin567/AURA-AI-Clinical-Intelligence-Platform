from pydantic import BaseModel
from typing import Dict, Any

class FeatureFlags(BaseModel):
    # Core OS
    enable_execution_graph: bool = True
    enable_workflow_engine: bool = True
    
    # Observability
    enable_observability: bool = True
    log_level: str = "INFO"
    enable_telemetry: bool = False
    
    # Prompts & Safety
    enable_prompt_versioning: bool = True
    enable_safety_pipeline: bool = True
    strict_clinical_safety: bool = True
    
    # Knowledge Platform
    enable_vector_search: bool = True
    enable_knowledge_ranking: bool = True
    enable_context_compression: bool = True
    enable_evidence_engine: bool = True
    enable_knowledge_graph: bool = True
    enable_dataset_pipeline: bool = True
    
    # Providers
    default_llm_provider: str = "openai"
    fallback_llm_provider: str = "gemini"

class CentralConfig:
    """Centralized configuration manager for AURA OS."""
    _features: FeatureFlags = FeatureFlags()
    
    @classmethod
    def features(cls) -> FeatureFlags:
        return cls._features
        
    @classmethod
    def update_features(cls, updates: Dict[str, Any]):
        current = cls._features.model_dump()
        current.update(updates)
        cls._features = FeatureFlags(**current)

features = CentralConfig.features()
