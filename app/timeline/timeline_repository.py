import abc
import os
import json
import threading
from typing import List, Optional
from datetime import datetime
from app.timeline.models import TimelineEntry

class TimelineRepository(abc.ABC):
    """
    Abstract interface for storing and retrieving patient timelines.
    """

    @abc.abstractmethod
    def add_entry(self, entry: TimelineEntry) -> None:
        pass

    @abc.abstractmethod
    def get_patient_timeline(self, patient_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[TimelineEntry]:
        pass


class InMemoryTimelineRepository(TimelineRepository):
    """
    In-memory storage for TimelineEntry instances.
    Supports querying and chronological sorting.
    """
    
    def __init__(self):
        self._storage: List[TimelineEntry] = []

    def add_entry(self, entry: TimelineEntry) -> None:
        self._storage.append(entry)

    def get_patient_timeline(self, patient_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[TimelineEntry]:
        # Filter by patient_id
        entries = [e for e in self._storage if e.patient_id == patient_id]

        # Filter by dates if provided
        if start_date:
            entries = [e for e in entries if e.timestamp >= start_date]
        if end_date:
            entries = [e for e in entries if e.timestamp <= end_date]

        # Sort chronologically (oldest to newest)
        entries.sort(key=lambda x: x.timestamp)
        return entries


class FileBasedTimelineRepository(TimelineRepository):
    """
    File-based storage for TimelineEntry instances.
    """
    def __init__(self, directory: str = "app/data/timeline"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self._lock = threading.Lock()

    def _get_path(self, patient_id: str) -> str:
        return os.path.join(self.directory, f"{patient_id}.json")

    def add_entry(self, entry: TimelineEntry) -> None:
        with self._lock:
            path = self._get_path(entry.patient_id)
            entries = []
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        data = json.load(f)
                        entries = [TimelineEntry.model_validate(e) for e in data]
                except Exception:
                    pass
            
            entries.append(entry)
            with open(path, "w") as f:
                json.dump([json.loads(e.model_dump_json()) for e in entries], f)

    def get_patient_timeline(self, patient_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[TimelineEntry]:
        with self._lock:
            path = self._get_path(patient_id)
            if not os.path.exists(path):
                return []
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    entries = [TimelineEntry.model_validate(e) for e in data]
            except Exception:
                return []

        # Filter by dates if provided
        if start_date:
            entries = [e for e in entries if e.timestamp >= start_date]
        if end_date:
            entries = [e for e in entries if e.timestamp <= end_date]

        # Sort chronologically (oldest to newest)
        entries.sort(key=lambda x: x.timestamp)
        return entries
