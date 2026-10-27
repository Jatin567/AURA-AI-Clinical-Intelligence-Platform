import time
from typing import Callable, Any
from app.observability.logger import logger

class ExecutionGraph:
    """Traces and monitors the execution of pipeline stages."""
    
    async def execute_node(self, node_name: str, session_id: str, func: Callable, *args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            latency_ms = (time.time() - start_time) * 1000
            logger.log_execution_trace(session_id, node_name, latency_ms)
            return result
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.log_execution_trace(session_id, f"{node_name}_ERROR", latency_ms)
            raise e

execution_graph = ExecutionGraph()
