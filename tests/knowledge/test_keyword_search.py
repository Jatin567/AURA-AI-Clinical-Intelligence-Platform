import pytest
from app.knowledge.retrieval.models import SearchRequest
from app.knowledge.retrieval.keyword_search import KeywordSearchEngine

def test_keyword_search():
    engine = KeywordSearchEngine()
    req = SearchRequest(query="chest pain", use_keyword=True)
    res = engine.search(req)
    assert len(res) > 0
    assert "chest" in res[0].text.lower()
