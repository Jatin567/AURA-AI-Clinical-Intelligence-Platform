from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class EmbeddingMetadata(BaseModel):
    dataset_id: str
    entity_id: Optional[str] = None
    taxonomy: Optional[str] = None
    priority: int = 10
    evidence_level: str = "Unknown"
    language: str = "en"
    embedding_dimension: int
    normalization: str = "L2"
    extra: Dict[str, Any] = Field(default_factory=dict)

class EmbeddingRecord(BaseModel):
    embedding_id: str
    chunk_id: str
    embedding_vector: List[float]
    model_name: str
    embedding_version: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    hash: str
    metadata: EmbeddingMetadata

class EmbeddingStatistics(BaseModel):
    total_embeddings: int = 0
    coverage_percentage: float = 0.0
    duplicate_count: int = 0
    dimensions: int = 0
    generation_time_ms: float = 0.0
    failures: int = 0
    model_usage: Dict[str, int] = Field(default_factory=dict)
