class CapabilityMetricsTracker:
    def __init__(self):
        self.metrics = {
            "workflow_latency": 0.0,
            "capability_latency": {},
            "critical_path_time": 0.0,
            "parallel_efficiency": 0.0,
            "failure_rate": 0.0,
            "retry_count": 0,
            "workflow_success_rate": 1.0
        }

    def record_capability_time(self, name: str, time_ms: float):
        self.metrics["capability_latency"][name] = time_ms

    def record_retry(self):
        self.metrics["retry_count"] += 1
