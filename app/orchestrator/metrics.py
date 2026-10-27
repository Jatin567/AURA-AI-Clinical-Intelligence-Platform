import time
from typing import Dict
from pydantic import BaseModel

class OrchestratorMetrics(BaseModel):
    retrieval_time_ms: float = 0.0
    memory_time_ms: float = 0.0
    prompt_time_ms: float = 0.0
    llm_time_ms: float = 0.0
    safety_time_ms: float = 0.0
    composer_time_ms: float = 0.0
    streaming_time_ms: float = 0.0
    tool_time_ms: float = 0.0
    total_time_ms: float = 0.0
    
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0.0
    cache_hits: int = 0

class MetricsTracker:
    def __init__(self):
        self.metrics = OrchestratorMetrics()
        self._timers: Dict[str, float] = {}

    def start_timer(self, name: str):
        self._timers[name] = time.time()

    def stop_timer(self, name: str):
        if name in self._timers:
            elapsed = (time.time() - self._timers[name]) * 1000
            setattr(self.metrics, f"{name}_time_ms", elapsed)
