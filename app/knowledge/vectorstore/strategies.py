from abc import ABC, abstractmethod
import numpy as np

class SimilarityStrategy(ABC):
    @abstractmethod
    def calculate(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        pass

class CosineSimilarity(SimilarityStrategy):
    def calculate(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return np.dot(vec_a, vec_b) / (norm_a * norm_b)

class DotProductSimilarity(SimilarityStrategy):
    def calculate(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        return np.dot(vec_a, vec_b)

class L2DistanceSimilarity(SimilarityStrategy):
    def calculate(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        return -float(np.linalg.norm(vec_a - vec_b))
