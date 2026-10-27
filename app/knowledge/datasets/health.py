import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from app.knowledge.core.interfaces import IHealthManager

class DatasetHealthManager(IHealthManager):
    """Tracks and updates dataset health metrics and lifecycle statuses."""
    
    def __init__(self, registry_path: str = "datasets/health_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"datasets": {}}

    def _save_registry(self) -> None:
        # Ensure parent directory exists
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, indent=2)

    def _ensure_dataset(self, dataset_id: str) -> None:
        if dataset_id not in self.registry["datasets"]:
            self.registry["datasets"][dataset_id] = {
                "metrics": {
                    "coverage": 0.0,
                    "missing_percentage": 0.0,
                    "duplicate_percentage": 0.0,
                    "null_percentage": 0.0,
                    "quality_score": 0.0
                },
                "status": {
                    "processing_status": "pending",
                    "embedding_status": "pending",
                    "index_status": "pending",
                    "knowledge_graph_status": "pending"
                },
                "last_validation": None
            }

    def update_status(self, dataset_id: str, status_key: str, status_value: str) -> None:
        self._ensure_dataset(dataset_id)
        if status_key in self.registry["datasets"][dataset_id]["status"]:
            self.registry["datasets"][dataset_id]["status"][status_key] = status_value
            self.registry["datasets"][dataset_id]["last_validation"] = datetime.utcnow().isoformat()
            self._save_registry()
        else:
            raise KeyError(f"Invalid status key: {status_key}")

    def update_metrics(self, dataset_id: str, metrics: Dict[str, Any]) -> None:
        self._ensure_dataset(dataset_id)
        for k, v in metrics.items():
            if k in self.registry["datasets"][dataset_id]["metrics"]:
                self.registry["datasets"][dataset_id]["metrics"][k] = v
        self.registry["datasets"][dataset_id]["last_validation"] = datetime.utcnow().isoformat()
        self._save_registry()

    def get_health_report(self, dataset_id: str) -> Dict[str, Any]:
        self._ensure_dataset(dataset_id)
        return self.registry["datasets"][dataset_id]

    def get_all_health(self) -> Dict[str, Any]:
        return self.registry["datasets"]
