from typing import Dict, Any

class RetrievalTelemetry:
    def log_event(self, event_name: str, payload: Dict[str, Any]) -> None:
        # Stub for Prometheus/Datadog logging
        pass
