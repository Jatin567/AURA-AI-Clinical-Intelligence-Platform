import pytest
from app.knowledge.taxonomy.hierarchy import TaxonomyManager

def test_taxonomy_manager():
    tm = TaxonomyManager()
    tm.populate_defaults()
    
    hierarchy = tm.get_hierarchy()
    assert len(hierarchy) > 0
    
    cardio = tm.get_node("sp_cardio")
    assert cardio is not None
    assert cardio.name == "Cardiology"
    assert any(c.id == "cat_arrhythmia" for c in cardio.children)
