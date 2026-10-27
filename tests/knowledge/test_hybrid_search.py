import pytest
from app.knowledge.retrieval.models import SearchRequest
from app.knowledge.retrieval.hybrid_search import HybridSearchEngine
from app.knowledge.retrieval.keyword_search import KeywordSearchEngine

class DummySemantic:
    def search(self, req): return []

class DummyGraph:
    def search(self, req): return []

def test_hybrid_search():
    semantic = DummySemantic()
    keyword = KeywordSearchEngine()
    graph = DummyGraph()
    hybrid = HybridSearchEngine(semantic, keyword, graph)
    
    req = SearchRequest(query="chest pain")
    res = hybrid.search(req)
    assert len(res) > 0
