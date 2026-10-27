import json
from typing import Iterator, Dict, Any, Optional

class DatasetCache:
    """Facilitates lazy loading, streaming reads, and caching for large datasets."""
    
    def __init__(self, max_cache_size_mb: int = 500):
        self.max_cache_size_mb = max_cache_size_mb
        self._memory_cache = {}

    def stream_jsonl(self, file_path: str) -> Iterator[Dict[str, Any]]:
        """Yields records lazily to prevent memory exhaustion."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
        except FileNotFoundError:
            return

    def get_cached_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        return self._memory_cache.get(record_id)

    def cache_record(self, record_id: str, record: Dict[str, Any]) -> None:
        # In a real scenario, we'd evict old entries if memory exceeds max_cache_size_mb.
        # For now, it's a simple dictionary cache.
        if len(self._memory_cache) < 10000: # Arbitrary record limit
            self._memory_cache[record_id] = record

    def clear_cache(self) -> None:
        self._memory_cache.clear()
