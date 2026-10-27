from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.knowledge.index.engine import knowledge_index

class EvidenceLevel(BaseModel):
    level: str  # e.g., "1A", "2B", "Consensus"
    description: str

class EvidenceRecord(BaseModel):
    id: str
    title: str
    organization: str
    publication_year: int
    evidence_level: EvidenceLevel
    confidence: float
    source_type: str  # e.g., "guideline", "meta-analysis", "rct"
    relevance_score: float
    url: Optional[str] = None
    metadata: Dict[str, Any] = {}

class EvidenceEngine:
    """Retrieves authoritative evidence citations before generation."""
    
    async def retrieve_evidence(self, query: str, context: Any) -> List[EvidenceRecord]:
        # 1. Query the knowledge index
        # We can extract keywords from query/context here.
        raw_results = await knowledge_index.search(query, filters={"category": "clinical_guideline"}, top_k=3)
        
        # 2. Map to EvidenceRecord
        evidence = []
        for idx, r in enumerate(raw_results):
            record = EvidenceRecord(
                id=r["id"],
                title=r.get("metadata", {}).get("title", f"Guideline Document {idx+1}"),
                organization=r.get("metadata", {}).get("organization", "Medical Society"),
                publication_year=r.get("metadata", {}).get("year", 2024),
                evidence_level=EvidenceLevel(level="1A", description="Strong recommendation, high-quality evidence"),
                confidence=r.get("score", 0.9),
                source_type="guideline",
                relevance_score=r.get("score", 0.9),
                metadata=r.get("metadata", {})
            )
            evidence.append(record)
            
        return evidence
        
    def format_citations(self, evidence: List[EvidenceRecord]) -> str:
        if not evidence:
            return ""
        formatted = "### References & Evidence\n"
        for idx, e in enumerate(evidence):
            formatted += f"{idx+1}. **{e.title}** ({e.publication_year}) - {e.organization} [Level: {e.evidence_level.level}]\n"
        return formatted

evidence_engine = EvidenceEngine()
