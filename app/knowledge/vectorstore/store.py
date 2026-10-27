from typing import List
import numpy as np
from app.knowledge.vectorstore.interfaces import VectorStore, IndexProvider

class VectorStoreImpl(VectorStore):
    """Implementation of VectorStore using an IndexProvider."""
    def __init__(self, provider: IndexProvider):
        self.provider = provider

    def batch_insert(self, embeddings: np.ndarray, ids: List[str]) -> None:
        self.provider.add(embeddings, ids)

    def batch_delete(self, ids: List[str]) -> None:
        self.provider.remove(ids)

    def nearest_neighbor_search(self, query: np.ndarray) -> List[str]:
        return self.top_k_search(query, 1)

    def top_k_search(self, query: np.ndarray, k: int) -> List[str]:
        distances, ids = self.provider.search(query, k)
        if ids and ids[0]:
            return ids[0]
        return []

    def reload_index(self) -> None:
        pass # Stub
