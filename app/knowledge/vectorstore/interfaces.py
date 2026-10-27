from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any
import numpy as np

class IndexProvider(ABC):
    """Decoupled interface for the underlying vector index technology (e.g. FAISS)."""
    @abstractmethod
    def add(self, embeddings: np.ndarray, ids: List[str]) -> None:
        pass

    @abstractmethod
    def remove(self, ids: List[str]) -> None:
        pass

    @abstractmethod
    def search(self, query_embedding: np.ndarray, k: int) -> Tuple[List[List[float]], List[List[str]]]:
        """Returns a tuple of (distances, ids)."""
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        pass

    @abstractmethod
    def load(self, path: str) -> None:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

class VectorStore(ABC):
    """High-level abstraction for vector store operations."""
    @abstractmethod
    def batch_insert(self, embeddings: np.ndarray, ids: List[str]) -> None:
        pass

    @abstractmethod
    def batch_delete(self, ids: List[str]) -> None:
        pass

    @abstractmethod
    def nearest_neighbor_search(self, query: np.ndarray) -> List[str]:
        pass

    @abstractmethod
    def top_k_search(self, query: np.ndarray, k: int) -> List[str]:
        pass

    @abstractmethod
    def reload_index(self) -> None:
        pass
