from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.knowledge.entities.registry import EntityRegistry
from app.knowledge.entities.resolver import EntityResolver
from app.knowledge.entities.synonyms import SynonymManager
from app.knowledge.entities.canonicalizer import Canonicalizer

router = APIRouter(prefix="/entities", tags=["entities"])

# Stub dependency injection
registry = EntityRegistry()
synonym_manager = SynonymManager()
canonicalizer = Canonicalizer(registry, synonym_manager)
resolver = EntityResolver(canonicalizer)

@router.get("/{entity_id}")
def get_entity(entity_id: str):
    """Retrieves canonical entity details."""
    entity = registry.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.post("/resolve")
def resolve_concept(source_dataset: str, source_id: str, domain: str, term: str):
    """Resolves a raw concept into a canonical AURA entity ID."""
    entity_id = resolver.resolve_concept(source_dataset, source_id, domain, term)
    return {"entity_id": entity_id}

@router.post("/synonyms")
def add_synonyms(domain: str, canonical_name: str, synonyms: List[str]):
    """Registers synonyms for a domain's canonical name."""
    synonym_manager.add_synonyms(domain, canonical_name, synonyms)
    return {"message": "Synonyms added"}
