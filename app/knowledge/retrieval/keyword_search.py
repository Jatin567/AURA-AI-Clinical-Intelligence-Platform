from typing import List
from app.knowledge.retrieval.interfaces import SearchEngine
from app.knowledge.retrieval.models import SearchRequest, SearchResult

class KeywordSearchEngine(SearchEngine):
    def __init__(self):
        # Stub BM25 index setup
        pass

    def search(self, request: SearchRequest) -> List[SearchResult]:
        if not request.use_keyword:
            return []
            
        # Stub keyword search (BM25)
        words = request.query.lower().split()
        
        results = []
        for i in range(min(request.top_k, 3)):
            res = SearchResult(
                chunk_id=f"kw_chunk_{i}",
                text=f"Keyword match containing {words[0] if words else 'term'}",
                score=0.8 - (i * 0.1),
                citation="keyword_source",
                provenance_type="keyword"
            )
            results.append(res)
            
        return results
