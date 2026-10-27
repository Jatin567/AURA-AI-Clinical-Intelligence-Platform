from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

class DatasetState(str, Enum):
    REGISTERED = "registered"
    VALIDATED = "validated"
    NORMALIZED = "normalized"
    CHUNKED = "chunked"
    EMBEDDED = "embedded"
    INDEXED = "indexed"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    FAILED = "failed"

class DatasetManifest(BaseModel):
    id: str
    name: str
    version: str
    source: str
    license: str
    checksum: str
    categories: List[str]
    language: str = "en"
    record_count: int = 0
    embedding_model: str = "local"
    update_frequency: str = "static"
    publication_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    state: DatasetState = DatasetState.REGISTERED
    metadata: Dict[str, Any] = {}
