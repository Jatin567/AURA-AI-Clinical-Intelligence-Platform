from typing import List
from app.knowledge.retrieval.interfaces import ContextCompressor
from app.knowledge.retrieval.models import SearchResult

class DocumentContextCompressor(ContextCompressor):
    """Compresses retrieved chunks to optimize token usage."""
    def compress(self, results: List[SearchResult]) -> str:
        compressed_text = ""
        for i, res in enumerate(results):
            compressed_text += f"[Citation: {res.citation}] {res.text}\n"
        return compressed_text
