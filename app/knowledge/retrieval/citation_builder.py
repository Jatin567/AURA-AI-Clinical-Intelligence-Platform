from typing import Dict, Any
from app.knowledge.retrieval.interfaces import CitationBuilder

class StructuredCitationBuilder(CitationBuilder):
    def build(self, metadata: Dict[str, Any]) -> str:
        dataset = metadata.get("dataset", "Unknown")
        publisher = metadata.get("publisher", "Unknown")
        version = metadata.get("version", "1.0")
        return f"{publisher}:{dataset} (v{version})"
