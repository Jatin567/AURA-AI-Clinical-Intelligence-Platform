from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class DatasetVersionInfo(BaseModel):
    version: str
    previous_version: Optional[str]
    migration_notes: str
    rollback_supported: bool

class DatasetVersionManager:
    """Manages version history, rollbacks, and migrations for datasets."""
    
    def __init__(self):
        self.version_history: Dict[str, List[DatasetVersionInfo]] = {}

    def register_version(self, dataset_id: str, version_info: DatasetVersionInfo) -> None:
        if dataset_id not in self.version_history:
            self.version_history[dataset_id] = []
        self.version_history[dataset_id].append(version_info)

    def get_latest_version(self, dataset_id: str) -> Optional[str]:
        history = self.version_history.get(dataset_id)
        if not history:
            return None
        return history[-1].version

    def check_compatibility(self, old_version: str, new_version: str) -> bool:
        """Determines if new_version is backwards compatible with old_version (semver logic)."""
        try:
            old_major = int(old_version.split(".")[0])
            new_major = int(new_version.split(".")[0])
            return old_major == new_major
        except (ValueError, IndexError):
            return False

    def get_rollback_target(self, dataset_id: str) -> Optional[str]:
        history = self.version_history.get(dataset_id)
        if history and len(history) > 1 and history[-1].rollback_supported:
            return history[-1].previous_version
        return None
