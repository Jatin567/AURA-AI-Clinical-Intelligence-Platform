from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ArtifactMetadata(BaseModel):
    confidence: float
    source: str
    page: int
    bounding_box: Optional[Dict[str, int]] = None
    processing_version: str

class ArtifactManifest(BaseModel):
    status: str = "UPLOADED"
    ocr: str = "PENDING"
    classifier: str = "PENDING"
    entities: str = "PENDING"
    relationships: str = "PENDING"
    timeline: str = "PENDING"
    retrieval_ready: bool = False
    errors: List[str] = Field(default_factory=list)

class MedicalArtifact(BaseModel):
    id: str
    filename: str
    version: int = 1
    artifact_type: str = "UNKNOWN"
    manifest: ArtifactManifest = Field(default_factory=ArtifactManifest)
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
