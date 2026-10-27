import pytest
import numpy as np
from app.knowledge.vectorstore.faiss_provider import FAISSProvider
from app.knowledge.vectorstore.store import VectorStoreImpl
from app.knowledge.vectorstore.strategies import CosineSimilarity
from app.knowledge.vectorstore.indexer import VectorIndexer
from app.knowledge.vectorstore.searcher import VectorSearcher

def test_faiss_provider():
    provider = FAISSProvider(dimension=2)
    embeddings = np.array([[1.0, 0.0], [0.0, 1.0]])
    ids = ["doc1", "doc2"]
    
    provider.add(embeddings, ids)
    assert provider.count() == 2
    
    distances, res_ids = provider.search(np.array([1.0, 0.0]), 1)
    assert len(res_ids[0]) == 1
    assert res_ids[0][0] == "doc1"
    
    provider.remove(["doc1"])
    assert provider.count() == 1

def test_vector_store():
    provider = FAISSProvider(dimension=2)
    store = VectorStoreImpl(provider)
    indexer = VectorIndexer(store)
    
    embeddings = np.array([[1.0, 0.0]])
    indexer.index_batch(embeddings, ["doc1"])
    
    searcher = VectorSearcher(store)
    results = searcher.search_top_k(np.array([1.0, 0.0]), 1)
    assert len(results) == 1
    assert results[0].chunk.chunk_id == "doc1"
