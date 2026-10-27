import re
from typing import List, Dict, Any
from app.knowledge.datasets.manifest import Chunk

class ChunkEngine:
    """Deterministic chunking engine without LLM or embeddings."""
    
    def __init__(self, strategy: str = "paragraph", max_tokens: int = 500):
        self.strategy = strategy
        self.max_tokens = max_tokens

    def _approximate_tokens(self, text: str) -> int:
        """Heuristic token count based on words."""
        return len(text.split())

    def _chunk_by_sentence(self, text: str) -> List[str]:
        # Simple regex split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s for s in sentences if s]

    def _chunk_by_paragraph(self, text: str) -> List[str]:
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]

    def _chunk_by_medical_section(self, text: str) -> List[str]:
        # Detect common medical headers like "Symptoms:", "Treatment:", etc.
        pattern = r'(?i)\n?(Symptoms|Treatment|Diagnosis|Causes|Risk Factors|Contraindications):'
        parts = re.split(pattern, text)
        chunks = []
        if parts:
            if parts[0].strip():
                chunks.append(parts[0].strip())
            for i in range(1, len(parts), 2):
                header = parts[i]
                content = parts[i+1] if i+1 < len(parts) else ""
                chunks.append(f"{header}:\n{content.strip()}")
        return chunks

    def process_record(self, record: Dict[str, Any]) -> List[Chunk]:
        """Convert a normalized record into chunks."""
        text = record.get("text", "")
        
        if self.strategy == "sentence":
            raw_chunks = self._chunk_by_sentence(text)
        elif self.strategy == "medical_section":
            raw_chunks = self._chunk_by_medical_section(text)
        else:
            raw_chunks = self._chunk_by_paragraph(text)
            
        chunks = []
        for i, rc in enumerate(raw_chunks):
            chunk = Chunk(
                chunk_id=f"{record['aura_id']}_chunk_{i}",
                parent_record=record['aura_id'],
                title=record.get("title", f"Chunk {i}"),
                text=rc,
                token_count=self._approximate_tokens(rc),
                category=record.get("category", "unknown"),
                priority=record.get("priority", 10),
                evidence_level=record.get("evidence_level", "Unknown"),
                dataset=record.get("dataset", "Unknown"),
                publisher=record.get("publisher", "Unknown"),
                metadata=record.get("metadata", {})
            )
            chunks.append(chunk)
            
        return chunks
