from typing import Dict, List, Any
from app.knowledge.entities.synonyms import SynonymManager
from app.knowledge.entities.registry import EntityRegistry

class Canonicalizer:
    """Maintains canonical disease, drug, symptom, lab, imaging, and guideline entities."""
    
    def __init__(self, registry: EntityRegistry, synonym_manager: SynonymManager):
        self.registry = registry
        self.synonym_manager = synonym_manager

    def canonicalize(self, domain: str, term: str) -> str:
        """
        Attempts to resolve a term to its canonical form using the SynonymManager.
        If not found, it treats the term itself as the canonical name (with simple normalization).
        Returns the immutable AURA entity ID.
        """
        canonical_name = self.synonym_manager.resolve(domain, term)
        if not canonical_name:
            canonical_name = term.strip().lower()
            
        return self.registry.register_entity(domain, canonical_name)
