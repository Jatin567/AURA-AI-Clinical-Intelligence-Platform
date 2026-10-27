import pytest
from app.knowledge.entities.registry import EntityRegistry
from app.knowledge.entities.synonyms import SynonymManager
from app.knowledge.entities.canonicalizer import Canonicalizer
from app.knowledge.entities.resolver import EntityResolver

def test_entity_resolution():
    registry = EntityRegistry()
    synonyms = SynonymManager()
    
    # Add synonym mapping
    synonyms.add_synonyms("disease", "Myocardial Infarction", ["Heart Attack", "MI"])
    
    canonicalizer = Canonicalizer(registry, synonyms)
    resolver = EntityResolver(canonicalizer)
    
    # Resolve synonymous concepts
    id1 = resolver.resolve_concept("ds1", "1", "disease", "Heart Attack")
    id2 = resolver.resolve_concept("ds2", "A", "disease", "MI")
    
    # They should resolve to the exact same immutable ID
    assert id1 == id2
    
    entity = registry.get_entity(id1)
    assert entity["name"] == "myocardial infarction"
