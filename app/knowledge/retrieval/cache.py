from typing import Dict, Optional, Any
import time

class RetrievalCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["data"]
            else:
                del self._cache[key]
        return None

    def set(self, key: str, data: Any) -> None:
        self._cache[key] = {
            "timestamp": time.time(),
            "data": data
        }
