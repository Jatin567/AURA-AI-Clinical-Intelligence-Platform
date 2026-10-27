from typing import Dict, Any, List
from app.knowledge.entities.canonicalizer import Canonicalizer

class EntityResolver:
    """Merges equivalent concepts across datasets."""
    
    def __init__(self, canonicalizer: Canonicalizer):
        self.canonicalizer = canonicalizer
        # Stores mappings of source_record_id to aura_entity_id
        self._concept_mappings: Dict[str, str] = {}
        
    def resolve_concept(self, source_dataset: str, source_id: str, domain: str, term: str) -> str:
        """
        Resolves a concept from a specific dataset into a canonical AURA entity.
        Records the lineage.
        """
        entity_id = self.canonicalizer.canonicalize(domain, term)
        
        mapping_key = f"{source_dataset}:{source_id}"
        self._concept_mappings[mapping_key] = entity_id
        
        return entity_id
        
    def get_resolved_entity(self, source_dataset: str, source_id: str) -> str:
        """Looks up an AURA entity ID based on a dataset and source record ID."""
        mapping_key = f"{source_dataset}:{source_id}"
        return self._concept_mappings.get(mapping_key)
