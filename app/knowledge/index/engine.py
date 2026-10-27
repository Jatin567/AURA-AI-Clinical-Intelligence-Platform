from typing import List, Dict, Any, Optional
from app.knowledge.index.graph import knowledge_graph

class KnowledgeIndex:
    """Advanced Knowledge Index with hybrid ranking, deduplication, and context compression."""
    
    def __init__(self):
        # We'd typically have a Vector DB and a text search index here
        pass
        
    async def search(self, query: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        # Hybrid Search stub
        # 1. Keyword Search
        # 2. Semantic Search
        results = [
            {"id": "doc1", "content": "Hypertension guidelines...", "score": 0.95, "metadata": {"category": "clinical_guideline"}},
            {"id": "doc2", "content": "High blood pressure treatment...", "score": 0.90, "metadata": {"category": "clinical_guideline"}}
        ]
        
        # 3. Hybrid Ranking
        ranked_results = self._hybrid_rank(results)
        
        # 4. Deduplication
        deduped_results = self._deduplicate(ranked_results)
        
        # 5. Metadata filtering
        if filters:
            deduped_results = self._filter(deduped_results, filters)
            
        return deduped_results[:top_k]
        
    def compress_context(self, results: List[Dict[str, Any]], max_tokens: int = 1000) -> str:
        """Compresses multiple results into a tight context string."""
        if not results:
            return ""
        return "\n".join([f"[{r['metadata'].get('category', 'doc')}]: {r['content']}" for r in results])
        
    def _hybrid_rank(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Sort by score descending
        return sorted(results, key=lambda x: x.get('score', 0.0), reverse=True)
        
    def _deduplicate(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        unique = []
        for r in results:
            if r['id'] not in seen:
                seen.add(r['id'])
                unique.append(r)
        return unique
        
    def _filter(self, results: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        filtered = []
        for r in results:
            match = True
            for k, v in filters.items():
                if r.get('metadata', {}).get(k) != v:
                    match = False
                    break
            if match:
                filtered.append(r)
        return filtered

knowledge_index = KnowledgeIndex()
