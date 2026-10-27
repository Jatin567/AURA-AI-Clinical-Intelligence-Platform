from typing import Dict, Optional, Any
import hashlib
import time

class PromptCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _hash(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, prompt_text: str) -> Optional[Any]:
        key = self._hash(prompt_text)
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["response"]
            else:
                del self._cache[key]
        return None

    def set(self, prompt_text: str, response: Any) -> None:
        key = self._hash(prompt_text)
        self._cache[key] = {
            "timestamp": time.time(),
            "response": response
        }
