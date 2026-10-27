from typing import Dict, Optional
from app.knowledge.embeddings.models import EmbeddingRecord

class EmbeddingCache:
    """Efficient caching of embeddings to avoid regenerating identical chunks."""
    def __init__(self):
        self._cache: Dict[str, EmbeddingRecord] = {}

    def get(self, chunk_hash: str) -> Optional[EmbeddingRecord]:
        return self._cache.get(chunk_hash)

    def set(self, chunk_hash: str, record: EmbeddingRecord) -> None:
        # LRU cache stub
        if len(self._cache) < 10000:
            self._cache[chunk_hash] = record

    def clear(self) -> None:
        self._cache.clear()
