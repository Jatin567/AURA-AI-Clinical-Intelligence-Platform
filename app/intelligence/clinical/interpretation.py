from typing import Dict, Any
from app.intelligence.coordinator.models import ClinicalContext
from app.knowledge.index.engine import knowledge_index

class ClinicalInterpretationEngine:
    """Interprets deterministic candidate conditions without diagnosing."""
    
    async def interpret(self, context: ClinicalContext) -> Dict[str, Any]:
        raw_candidates = context.clinical_reasoning_output.get("candidates", [])
        
        interpreted = []
        for c in raw_candidates:
            # Query knowledge graph/index for context
            knowledge = await knowledge_index.search(c.get("name", ""))
            interpreted.append({
                "condition": c.get("name"),
                "base_probability": c.get("probability", 0),
                "knowledge_support": len(knowledge) > 0,
                "interpretation": f"Condition matches {len(knowledge)} knowledge records."
            })
            
        return {"interpreted_candidates": interpreted}

clinical_interpretation_engine = ClinicalInterpretationEngine()
