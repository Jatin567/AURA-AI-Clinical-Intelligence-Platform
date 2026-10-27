from typing import Dict
from app.knowledge.vectorstore.models import VectorStatistics

class VectorRepository:
    """Manages raw vector indices metadata."""
    def __init__(self):
        self._stats: Dict[str, VectorStatistics] = {}

    def save_stats(self, index_name: str, stats: VectorStatistics) -> None:
        self._stats[index_name] = stats

    def get_stats(self, index_name: str) -> VectorStatistics:
        return self._stats.get(index_name, VectorStatistics())
