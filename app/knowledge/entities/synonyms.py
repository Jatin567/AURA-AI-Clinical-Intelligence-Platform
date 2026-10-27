from typing import Dict, List, Optional

class SynonymManager:
    """Deterministically resolves synonyms and abbreviations."""
    
    def __init__(self):
        # Maps domain -> normalized synonym -> canonical_name
        self._synonym_map: Dict[str, Dict[str, str]] = {} 
    
    def _normalize(self, text: str) -> str:
        return text.strip().lower()

    def add_synonyms(self, domain: str, canonical_name: str, synonyms: List[str]) -> None:
        """Registers a canonical name and its synonyms for a domain."""
        if domain not in self._synonym_map:
            self._synonym_map[domain] = {}
        
        norm_canonical = self._normalize(canonical_name)
        # Canonical name resolves to itself
        self._synonym_map[domain][norm_canonical] = norm_canonical
        
        for syn in synonyms:
            self._synonym_map[domain][self._normalize(syn)] = norm_canonical
            
    def resolve(self, domain: str, term: str) -> Optional[str]:
        """Resolves a term to its canonical name if known."""
        if domain not in self._synonym_map:
            return None
        return self._synonym_map[domain].get(self._normalize(term))
