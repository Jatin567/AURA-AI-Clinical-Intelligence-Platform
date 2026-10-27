from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    filters: Dict[str, Any] = Field(default_factory=dict)
    use_semantic: bool = True
    use_keyword: bool = True
    use_graph: bool = True
    request_id: str = Field(default_factory=lambda: f"req_{int(datetime.utcnow().timestamp())}")

class SearchResult(BaseModel):
    chunk_id: str
    text: str
    score: float
    citation: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    provenance_type: str = "semantic" # semantic, keyword, graph, hybrid

class EvidencePackage(BaseModel):
    request_id: str
    original_query: str
    expanded_queries: List[str]
    results: List[SearchResult]
    compressed_context: str
    retrieval_metadata: Dict[str, Any] = Field(default_factory=dict)

class RetrievalStatistics(BaseModel):
    total_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_latency_ms: float = 0.0
    avg_results_returned: float = 0.0
    avg_compression_ratio: float = 0.0

class RetrievalMetadata(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    latency_ms: float = 0.0
    strategy_used: str = "hybrid"
    entities_linked: List[str] = Field(default_factory=list)
