import time
from typing import Dict, Any

class RAGMetricsTracker:
    """Deep telemetry tracking across RAG layers."""
    def __init__(self):
        self.timers: Dict[str, float] = {}
        self.metrics: Dict[str, Any] = {
            "intent": "unknown",
            "workflow": "unknown",
            "provider": "unknown",
            "retrievals_count": 0,
            "retrieval_time": 0.0,
            "embedding_time": 0.0,
            "ranking_time": 0.0,
            "compression_time": 0.0,
            "prompt_build_time": 0.0,
            "llm_time": 0.0,
            "safety_time": 0.0,
            "composer_time": 0.0,
            "total_rag_time": 0.0,
            "tokens": 0,
            "cost": 0.0,
            "cache_hits": 0,
            "confidence": 0.0
        }

    def start_timer(self, name: str):
        self.timers[name] = time.time()

    def stop_timer(self, name: str):
        if name in self.timers:
            elapsed = (time.time() - self.timers[name]) * 1000
            self.metrics[name] += elapsed

    def record(self, key: str, value: Any):
        self.metrics[key] = value

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics
