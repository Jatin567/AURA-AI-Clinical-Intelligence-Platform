from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.knowledge.taxonomy.hierarchy import TaxonomyManager

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])

taxonomy_manager = TaxonomyManager()
taxonomy_manager.populate_defaults()

@router.get("/")
def get_taxonomy():
    """Returns the full deterministic taxonomy hierarchy."""
    return taxonomy_manager.get_hierarchy()

@router.get("/{node_id}")
def get_node(node_id: str):
    """Returns details for a specific taxonomy node."""
    node = taxonomy_manager.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Taxonomy node not found")
    return node.to_dict()
