import asyncio
import logging
from typing import List, Dict, Any, Tuple
from app.capabilities.core.interfaces import ICapability

logger = logging.getLogger(__name__)

class ExecutionCoordinator:
    """Manages parallel execution, retries, fallbacks, and timeouts."""
    
    async def execute_parallel(self, capabilities: List[Tuple[ICapability, Dict[str, Any]]], timeout_s: int = 10) -> List[Dict[str, Any]]:
        tasks = []
        for capability, inputs in capabilities:
            # Wrap execution with retry/timeout logic
            task = asyncio.create_task(self._execute_with_policy(capability, inputs, timeout_s))
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def _execute_with_policy(self, capability: ICapability, inputs: Dict[str, Any], timeout_s: int) -> Dict[str, Any]:
        retries = 2
        for attempt in range(retries):
            try:
                # Enforce timeout policy
                return await asyncio.wait_for(capability.execute(inputs), timeout=timeout_s)
            except asyncio.TimeoutError:
                logger.warning(f"Capability {capability.get_metadata().name} timed out.")
                if attempt == retries - 1:
                    return {"status": "error", "message": "Timeout"}
            except Exception as e:
                logger.error(f"Capability {capability.get_metadata().name} failed: {e}")
                if attempt == retries - 1:
                    return {"status": "error", "message": str(e)}
        return {"status": "error"}
