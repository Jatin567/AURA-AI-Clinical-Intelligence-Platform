from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass

class LocalSentenceTransformerProvider(EmbeddingProvider):
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def embed(self, text: str) -> List[float]:
        # Stub implementation
        return [0.0] * self.dimension

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        # Stub implementation
        return [[0.0] * self.dimension for _ in texts]
