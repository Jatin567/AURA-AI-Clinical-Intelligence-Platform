import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.knowledge.embeddings.provider import EmbeddingProvider
from app.knowledge.embeddings.models import EmbeddingRecord, EmbeddingMetadata
from app.knowledge.embeddings.manager import EmbeddingModelManager
from app.knowledge.datasets.manifest import Chunk

class EmbeddingPipeline:
    """Pipeline for batch embedding generation with incremental processing."""
    def __init__(self, provider: EmbeddingProvider, manager: EmbeddingModelManager):
        self.provider = provider
        self.manager = manager

    def _generate_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def process_chunks(self, chunks: List[Chunk], dataset_id: str) -> List[EmbeddingRecord]:
        """Processes chunks incrementally; caller should check cache first."""
        texts = [chunk.text for chunk in chunks]
        vectors = self.provider.embed_batch(texts)
        
        active_model = self.manager.get_active_model()
        model_name = active_model.name if active_model else "unknown"
        dimensions = active_model.dimensions if active_model else len(vectors[0])

        records = []
        for i, chunk in enumerate(chunks):
            metadata = EmbeddingMetadata(
                dataset_id=dataset_id,
                priority=chunk.priority,
                evidence_level=chunk.evidence_level,
                embedding_dimension=dimensions
            )
            
            record = EmbeddingRecord(
                embedding_id=f"emb_{chunk.chunk_id}",
                chunk_id=chunk.chunk_id,
                embedding_vector=vectors[i],
                model_name=model_name,
                embedding_version="1.0",
                hash=self._generate_hash(chunk.text),
                metadata=metadata
            )
            records.append(record)
            
        return records
