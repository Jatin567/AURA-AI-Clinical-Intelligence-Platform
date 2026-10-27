from typing import List
from app.knowledge.retrieval.models import SearchResult

class EvidenceSelector:
    """Selects highest quality evidence and removes duplicates."""
    def select(self, results: List[SearchResult]) -> List[SearchResult]:
        seen = set()
        unique = []
        for res in results:
            if res.chunk_id not in seen:
                seen.add(res.chunk_id)
                unique.append(res)
        return unique
