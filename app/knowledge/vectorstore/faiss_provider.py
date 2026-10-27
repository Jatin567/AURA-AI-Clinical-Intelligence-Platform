from typing import List, Tuple
import numpy as np
from app.knowledge.vectorstore.interfaces import IndexProvider

class FAISSProvider(IndexProvider):
    """FAISS implementation of IndexProvider."""
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self._ids: List[str] = []
        self._embeddings: List[List[float]] = [] # Stub for FAISS index

    def add(self, embeddings: np.ndarray, ids: List[str]) -> None:
        for i, emb in enumerate(embeddings):
            self._embeddings.append(emb.tolist())
            self._ids.append(ids[i])

    def remove(self, ids: List[str]) -> None:
        indices_to_remove = []
        for i, existing_id in enumerate(self._ids):
            if existing_id in ids:
                indices_to_remove.append(i)
        
        # Remove in reverse to maintain indices
        for i in reversed(indices_to_remove):
            self._ids.pop(i)
            self._embeddings.pop(i)

    def search(self, query_embedding: np.ndarray, k: int) -> Tuple[List[List[float]], List[List[str]]]:
        if not self._embeddings:
            return [[]], [[]]
            
        distances = []
        for emb in self._embeddings:
            dist = -float(np.linalg.norm(query_embedding - np.array(emb)))
            distances.append(dist)
            
        top_k_indices = np.argsort(distances)[-k:][::-1]
        
        top_distances = [distances[i] for i in top_k_indices]
        top_ids = [self._ids[i] for i in top_k_indices]
        
        return [top_distances], [top_ids]

    def save(self, path: str) -> None:
        pass # Stub

    def load(self, path: str) -> None:
        pass # Stub

    def count(self) -> int:
        return len(self._ids)
