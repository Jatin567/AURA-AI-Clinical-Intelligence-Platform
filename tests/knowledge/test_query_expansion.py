import pytest
from app.knowledge.retrieval.query_expander import SynonymsQueryExpander

def test_query_expander():
    expander = SynonymsQueryExpander()
    res = expander.expand("I have chest pain")
    assert "chest pain" in res[0]
    assert "angina" in res
    assert "cardiac chest pain" in res
