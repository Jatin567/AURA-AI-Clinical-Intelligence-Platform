import pytest
import time
from app.knowledge.retrieval.cache import RetrievalCache

def test_retrieval_cache():
    cache = RetrievalCache(ttl_seconds=1)
    cache.set("q1", {"results": [1, 2, 3]})
    assert cache.get("q1") is not None
    time.sleep(1.1)
    assert cache.get("q1") is None
