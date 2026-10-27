import pytest
from app.knowledge.retrieval.filters import RetrievalFilter
from app.knowledge.retrieval.models import SearchResult

def test_retrieval_filters():
    f = RetrievalFilter()
    r1 = SearchResult(chunk_id="1", text="a", score=1.0, citation="c", metadata={"lang": "en"})
    r2 = SearchResult(chunk_id="2", text="b", score=1.0, citation="c", metadata={"lang": "es"})
    
    filtered = f.filter([r1, r2], {"lang": "en"})
    assert len(filtered) == 1
    assert filtered[0].chunk_id == "1"
