from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from app.knowledge.datasets.manifest import Chunk

class VectorStatistics(BaseModel):
    index_size: int = 0
    dimensions: int = 0
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    index_version: str = "1.0"
    model_name: str = "unknown"

class RetrievalResult(BaseModel):
    chunk: Chunk
    similarity: float
    priority: int
    evidence_level: str
    dataset: str
    citation: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Extended for future Hybrid Retrieval
    entity_id: Optional[str] = None
    dataset_version: Optional[str] = None
    taxonomy: Optional[str] = None
    knowledge_score: float = 0.0
    retrieval_metadata: Dict[str, Any] = Field(default_factory=dict)
