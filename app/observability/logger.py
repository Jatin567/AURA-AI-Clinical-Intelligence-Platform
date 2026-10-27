import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict

class AURAObservabilityLogger:
    """Centralized observability logger for AURA OS."""
    
    def __init__(self):
        self.logger = logging.getLogger("aura.os")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log_event(self, event_type: str, session_id: str, details: Dict[str, Any]):
        """Logs structured domain events."""
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "session_id": session_id,
            "details": details
        }
        self.logger.info(json.dumps(payload))
        
    def log_safety_event(self, session_id: str, flag: str, severity: str):
        self.log_event("SAFETY_VIOLATION", session_id, {"flag": flag, "severity": severity})

    def log_execution_trace(self, session_id: str, stage: str, latency_ms: float):
        self.log_event("EXECUTION_TRACE", session_id, {"stage": stage, "latency_ms": latency_ms})
        
    def log_llm_usage(self, session_id: str, provider: str, model: str, prompt_tokens: int, completion_tokens: int):
        self.log_event("LLM_USAGE", session_id, {
            "provider": provider,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens
        })

logger = AURAObservabilityLogger()
