from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class IDatasetRegistry(ABC):
    """Abstract interface for dataset registration and tracking."""
    
    @abstractmethod
    def register(self, manifest: BaseModel) -> None:
        pass

    @abstractmethod
    def get_dataset(self, dataset_id: str) -> Optional[BaseModel]:
        pass

    @abstractmethod
    def list_datasets(self) -> List[BaseModel]:
        pass

    @abstractmethod
    def detect_duplicates(self) -> List[str]:
        pass


class IDatasetRepository(ABC):
    """Abstract interface for storing and retrieving dataset records and chunks."""
    
    @abstractmethod
    def save_record(self, dataset_id: str, record: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def save_chunk(self, chunk: Dict[str, Any]) -> None:
        pass


class IHealthManager(ABC):
    """Abstract interface for tracking dataset health metrics."""
    
    @abstractmethod
    def update_status(self, dataset_id: str, status_key: str, status_value: str) -> None:
        pass

    @abstractmethod
    def update_metrics(self, dataset_id: str, metrics: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_health_report(self, dataset_id: str) -> Dict[str, Any]:
        pass


class IPriorityManager(ABC):
    """Abstract interface for resolving knowledge precedence."""
    
    @abstractmethod
    def get_priority(self, publisher: str) -> int:
        pass

    @abstractmethod
    def compare(self, source_a: str, source_b: str) -> int:
        pass

    @abstractmethod
    def resolve_conflict(self, facts: List[Dict[str, Any]]) -> Dict[str, Any]:
        pass


class IStorage(ABC):
    """Abstract interface for file and object storage (supports future S3 migration)."""
    
    @abstractmethod
    def write_file(self, path: str, content: bytes) -> None:
        pass

    @abstractmethod
    def read_file(self, path: str) -> bytes:
        pass

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        pass
