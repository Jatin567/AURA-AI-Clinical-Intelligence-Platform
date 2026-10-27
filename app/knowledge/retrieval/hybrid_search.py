from typing import List, Dict
from app.knowledge.retrieval.interfaces import SearchEngine
from app.knowledge.retrieval.models import SearchRequest, SearchResult

class HybridSearchEngine(SearchEngine):
    def __init__(self, 
                 semantic_engine: SearchEngine, 
                 keyword_engine: SearchEngine,
                 graph_engine: SearchEngine):
        self.semantic = semantic_engine
        self.keyword = keyword_engine
        self.graph = graph_engine

    def search(self, request: SearchRequest) -> List[SearchResult]:
        semantic_results = self.semantic.search(request)
        keyword_results = self.keyword.search(request)
        graph_results = self.graph.search(request)
        
        # Merge results, deduplicate by chunk_id, keep highest score or combine
        merged: Dict[str, SearchResult] = {}
        
        for res in semantic_results + keyword_results + graph_results:
            if res.chunk_id not in merged:
                merged[res.chunk_id] = res
            else:
                # Combine scores (simple additive stub)
                merged[res.chunk_id].score += res.score
                merged[res.chunk_id].provenance_type = "hybrid"
                
        return list(merged.values())
