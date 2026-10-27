from typing import Dict, Any

class CitationManager:
    """Upgraded citation handling supporting publishers (WHO, NIH, etc)."""
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        publisher = metadata.get("publisher", "Unknown")
        evidence_level = metadata.get("evidence_level", "Low")
        confidence = metadata.get("confidence", 0.0)
        return f"[{publisher}] (Level {evidence_level}, Conf {confidence:.2f})"
