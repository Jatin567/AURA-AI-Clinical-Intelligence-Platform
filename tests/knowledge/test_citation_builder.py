import pytest
from app.knowledge.retrieval.citation_builder import StructuredCitationBuilder

def test_citation_builder():
    builder = StructuredCitationBuilder()
    cit = builder.build({"dataset": "DS1", "publisher": "WHO", "version": "1.2"})
    assert cit == "WHO:DS1 (v1.2)"
