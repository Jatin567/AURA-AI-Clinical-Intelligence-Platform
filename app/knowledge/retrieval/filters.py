from typing import List
from app.knowledge.retrieval.models import SearchResult

class RetrievalFilter:
    def filter(self, results: List[SearchResult], criteria: dict) -> List[SearchResult]:
        filtered = []
        for res in results:
            match = True
            for k, v in criteria.items():
                if res.metadata.get(k) != v:
                    match = False
                    break
            if match:
                filtered.append(res)
        return filtered
