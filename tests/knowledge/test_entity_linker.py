import pytest
from app.knowledge.retrieval.entity_linker import RegistryEntityLinker

def test_entity_linker():
    linker = RegistryEntityLinker()
    entities = linker.link("patient has severe chest pain")
    assert "AURA_ENT_001" in entities
