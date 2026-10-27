from typing import List, Dict, Any
from app.knowledge.core.interfaces import IPriorityManager

class DatasetPriorityManager(IPriorityManager):
    """Deterministic priority manager enforcing knowledge precedence."""
    
    PRIORITY_MAP = {
        "WHO": 100,
        "CDC": 95,
        "NICE": 94,
        "NIH": 93,
        "Peer-reviewed Guidelines": 90,
        "Clinical Trials": 80,
        "Research Papers": 70,
        "Educational Sources": 50,
        "Unknown": 10
    }
    
    EVIDENCE_LEVELS = {
        100: "Level 1: Global Health Authority",
        95: "Level 1: National Health Authority",
        94: "Level 1: National Health Authority",
        93: "Level 1: National Health Authority",
        90: "Level 2: Medical Society Guideline",
        80: "Level 3: Clinical Trial",
        70: "Level 4: Peer-reviewed Research",
        50: "Level 5: Educational / Textbook",
        10: "Level 6: Unverified"
    }

    def get_priority(self, publisher: str) -> int:
        return self.PRIORITY_MAP.get(publisher, self.PRIORITY_MAP["Unknown"])

    def get_evidence_level(self, priority: int) -> str:
        # Fallback to closest lower evidence level
        sorted_levels = sorted(self.EVIDENCE_LEVELS.items(), reverse=True)
        for p, level in sorted_levels:
            if priority >= p:
                return level
        return self.EVIDENCE_LEVELS[10]

    def compare(self, source_a: str, source_b: str) -> int:
        """Returns positive if source_a > source_b, negative if source_b > source_a, 0 if equal."""
        return self.get_priority(source_a) - self.get_priority(source_b)

    def resolve_conflict(self, facts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolves conflict by picking the highest priority source."""
        if not facts:
            raise ValueError("No facts provided to resolve.")
            
        def _get_fact_priority(fact):
            publisher = fact.get("publisher", "Unknown")
            return self.get_priority(publisher)
            
        return max(facts, key=_get_fact_priority)
