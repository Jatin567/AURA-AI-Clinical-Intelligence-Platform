from typing import List
from app.knowledge.retrieval.interfaces import CrossEncoderReranker
from app.knowledge.retrieval.models import SearchResult

class DummyReranker(CrossEncoderReranker):
    def rerank(self, query: str, results: List[SearchResult]) -> List[SearchResult]:
        # Sort by existing score as a fallback
        return sorted(results, key=lambda x: x.score, reverse=True)
