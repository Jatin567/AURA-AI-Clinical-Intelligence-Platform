from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.knowledge.datasets.registry import DatasetRegistry
from app.knowledge.datasets.health import DatasetHealthManager
from app.knowledge.datasets.priority import DatasetPriorityManager

router = APIRouter(prefix="/datasets", tags=["datasets"])

# In a real app, these would be injected via FastAPI dependencies
registry = DatasetRegistry()
health_manager = DatasetHealthManager()
priority_manager = DatasetPriorityManager()

@router.get("/")
def list_datasets():
    """Returns the list of all registered datasets."""
    return registry.list_datasets()

@router.get("/{dataset_id}/manifest")
def get_manifest(dataset_id: str):
    """Returns the manifest for a specific dataset."""
    dataset = registry.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.get("/health")
def get_all_health():
    """Returns health statistics for all datasets."""
    return health_manager.get_all_health()

@router.get("/{dataset_id}/health")
def get_health(dataset_id: str):
    """Returns health statistics for a specific dataset."""
    try:
        return health_manager.get_health_report(dataset_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Health report not found")

@router.get("/statistics")
def get_statistics():
    """Returns aggregated statistics across the entire knowledge platform."""
    # Read from datasets/statistics_registry.json
    import json
    from pathlib import Path
    stat_path = Path("datasets/statistics_registry.json")
    if stat_path.exists():
        with open(stat_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"message": "No statistics available"}

@router.get("/categories")
def get_categories():
    """Returns distinct medical categories in the registry."""
    categories = set(d.category for d in registry.list_datasets() if hasattr(d, 'category'))
    return list(categories)

@router.get("/publishers")
def get_publishers():
    """Returns recognized publishers and their priority scores."""
    return priority_manager.PRIORITY_MAP

@router.get("/{dataset_id}/relationships")
def get_relationships(dataset_id: str):
    """Returns extracted relationships for a given dataset."""
    # Stub: Would normally query the graph or relationships store
    return {"dataset_id": dataset_id, "relationships": []}

@router.get("/{dataset_id}/chunks")
def get_chunks(dataset_id: str):
    """Returns generated chunks for a given dataset."""
    # Stub: Would normally query the chunk store
    return {"dataset_id": dataset_id, "chunks": []}
