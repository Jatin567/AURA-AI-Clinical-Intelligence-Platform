from typing import List, Any
import numpy as np
from app.knowledge.retrieval.interfaces import SearchEngine
from app.knowledge.retrieval.models import SearchRequest, SearchResult
from app.knowledge.vectorstore.interfaces import VectorStore
from app.knowledge.embeddings.provider import EmbeddingProvider

class SemanticSearchEngine(SearchEngine):
    def __init__(self, vector_store: VectorStore, embedder: EmbeddingProvider):
        self.vector_store = vector_store
        self.embedder = embedder

    def search(self, request: SearchRequest) -> List[SearchResult]:
        if not request.use_semantic:
            return []
            
        # Get query embedding
        query_vector = self.embedder.embed(request.query)
        
        # Search vector store
        top_ids = self.vector_store.top_k_search(np.array(query_vector), request.top_k)
        
        results = []
        for i, chunk_id in enumerate(top_ids):
            # Stub mapping to SearchResult
            res = SearchResult(
                chunk_id=chunk_id,
                text=f"Semantic match for {chunk_id}",
                score=0.9 - (i * 0.05), # Stub score decay
                citation="semantic_source",
                provenance_type="semantic"
            )
            results.append(res)
            
        return results
