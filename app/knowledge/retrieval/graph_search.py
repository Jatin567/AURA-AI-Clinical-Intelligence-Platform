from typing import List
from app.knowledge.retrieval.interfaces import SearchEngine, KnowledgeGraphSearcher
from app.knowledge.retrieval.models import SearchRequest, SearchResult

class GraphSearchEngine(SearchEngine):
    def __init__(self, graph_searcher: KnowledgeGraphSearcher):
        self.graph_searcher = graph_searcher

    def search(self, request: SearchRequest) -> List[SearchResult]:
        if not request.use_graph:
            return []
            
        # Stub entity extraction from query
        entities = request.query.split()
        return self.graph_searcher.search_graph(entities)
