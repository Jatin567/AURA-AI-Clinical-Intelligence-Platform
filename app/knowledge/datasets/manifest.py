from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class DatasetManifest(BaseModel):
    """The 27-field Master Manifest for all AURA datasets."""
    dataset_id: str
    name: str
    publisher: str
    license: str
    version: str
    release_date: str
    checksum_sha256: str
    processing_version: str
    embedding_version: str
    knowledge_version: str
    language: str
    country: str
    medical_domain: str
    dataset_type: str
    priority: int
    evidence_level: str
    quality_score: float
    processing_status: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Extended fields
    record_count: int = 0
    chunk_count: int = 0
    relationship_count: int = 0
    graph_ready: bool = False
    embedding_ready: bool = False
    publisher_url: Optional[str] = None


class NormalizedRecord(BaseModel):
    """The 15-field normalized record schema."""
    aura_id: str
    title: str
    text: str
    category: str
    dataset: str
    dataset_version: str
    publisher: str
    source_url: Optional[str] = None
    evidence_level: str
    priority: int
    confidence: float
    language: str
    metadata: Dict[str, Any]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    processing_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Chunk(BaseModel):
    """The 11-field chunk schema prepared for future embedding pipelines."""
    chunk_id: str
    parent_record: str
    title: str
    text: str
    token_count: int
    category: str
    priority: int
    evidence_level: str
    dataset: str
    publisher: str
    metadata: Dict[str, Any]
