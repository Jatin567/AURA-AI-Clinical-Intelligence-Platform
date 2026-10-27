import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel
from app.knowledge.core.interfaces import IDatasetRegistry
from app.knowledge.datasets.manifest import DatasetManifest

class DatasetRegistry(IDatasetRegistry):
    """Central registry tracking dataset classification, duplication, and metadata."""
    
    def __init__(self, registry_path: str = "datasets/registry.json"):
        self.registry_path = Path(registry_path)
        self.datasets: Dict[str, DatasetManifest] = {}
        self._load()

    def _load(self) -> None:
        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for d in data.get("datasets", []):
                    try:
                        self.datasets[d["dataset_id"]] = DatasetManifest(**d)
                    except Exception:
                        pass # Ignore invalid legacy entries during load

    def _save(self) -> None:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"datasets": [d.model_dump() for d in self.datasets.values()]}
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def register(self, manifest: DatasetManifest) -> None:
        self.datasets[manifest.dataset_id] = manifest
        self._save()

    def get_dataset(self, dataset_id: str) -> Optional[DatasetManifest]:
        return self.datasets.get(dataset_id)

    def list_datasets(self) -> List[DatasetManifest]:
        return list(self.datasets.values())

    def detect_duplicates(self) -> List[str]:
        seen_checksums = set()
        duplicates = []
        for d in self.datasets.values():
            if d.checksum_sha256 in seen_checksums:
                duplicates.append(d.dataset_id)
            else:
                seen_checksums.add(d.checksum_sha256)
        return duplicates

dataset_registry = DatasetRegistry()
