import pytest
from app.knowledge.retrieval.context_compressor import DocumentContextCompressor
from app.knowledge.retrieval.models import SearchResult

def test_context_compressor():
    comp = DocumentContextCompressor()
    res1 = SearchResult(chunk_id="1", text="Test evidence.", score=0.9, citation="WHO:DS1")
    compressed = comp.compress([res1])
    assert "[Citation: WHO:DS1] Test evidence." in compressed
