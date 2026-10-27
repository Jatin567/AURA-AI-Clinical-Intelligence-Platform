import pytest
from app.knowledge.retrieval.models import SearchRequest
from app.knowledge.retrieval.semantic_search import SemanticSearchEngine
from app.knowledge.vectorstore.store import VectorStoreImpl
from app.knowledge.vectorstore.faiss_provider import FAISSProvider
from app.knowledge.embeddings.provider import LocalSentenceTransformerProvider

def test_semantic_search():
    provider = FAISSProvider(dimension=2)
    store = VectorStoreImpl(provider)
    embedder = LocalSentenceTransformerProvider(dimension=2)
    engine = SemanticSearchEngine(store, embedder)
    
    req = SearchRequest(query="test", use_semantic=True)
    res = engine.search(req)
    assert isinstance(res, list)
