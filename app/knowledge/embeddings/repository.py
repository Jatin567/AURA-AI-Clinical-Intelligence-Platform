from typing import Dict, List, Optional
from app.knowledge.embeddings.models import EmbeddingRecord

class EmbeddingRepository:
    """Stores embeddings separately from chunks."""
    def __init__(self):
        # Stub DB
        self._records: Dict[str, EmbeddingRecord] = {}

    def save(self, record: EmbeddingRecord) -> None:
        self._records[record.embedding_id] = record

    def save_batch(self, records: List[EmbeddingRecord]) -> None:
        for r in records:
            self.save(r)

    def get(self, embedding_id: str) -> Optional[EmbeddingRecord]:
        return self._records.get(embedding_id)
        
    def get_by_chunk_id(self, chunk_id: str) -> Optional[EmbeddingRecord]:
        for record in self._records.values():
            if record.chunk_id == chunk_id:
                return record
        return None
