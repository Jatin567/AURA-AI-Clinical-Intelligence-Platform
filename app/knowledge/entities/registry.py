import hashlib
from typing import Dict, Any, Optional

class EntityRegistry:
    """Assigns and manages immutable AURA entity IDs."""
    
    def __init__(self):
        # In a real system, this would be backed by a DB or persistent file
        self._entities: Dict[str, Dict[str, Any]] = {}
    
    def generate_id(self, domain: str, name: str) -> str:
        """Generates a deterministic immutable ID based on domain and canonical name."""
        canonical_string = f"aura:{domain}:{name.strip().lower()}"
        return hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()[:16]

    def register_entity(self, domain: str, name: str, metadata: Dict[str, Any] = None) -> str:
        """Registers a new entity if it doesn't exist and returns its ID."""
        entity_id = self.generate_id(domain, name)
        if entity_id not in self._entities:
            self._entities[entity_id] = {
                "id": entity_id,
                "domain": domain,
                "name": name.strip().lower(),
                "metadata": metadata or {}
            }
        elif metadata:
            # Update metadata if provided and entity exists
            self._entities[entity_id]["metadata"].update(metadata)
            
        return entity_id
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an entity by its AURA ID."""
        return self._entities.get(entity_id)
