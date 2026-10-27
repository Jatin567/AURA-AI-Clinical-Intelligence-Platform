from typing import Dict, Any, List
from app.orchestrator.plugins import plugin_discovery
from app.observability.logger import logger

class WorkflowEngine:
    def __init__(self):
        pass
        
    async def execute_workflow(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a structured workflow of plugins based on intent."""
        plugins = plugin_discovery.get_plugins_for_intent(intent)
        workflow_results = {}
        
        for plugin in plugins:
            logger.log_execution_trace(context.get("session_id", "unknown"), f"plugin_{plugin.id}", 0.0)
            result = await plugin.execute(context)
            workflow_results[plugin.id] = result
            
        return workflow_results

workflow_engine = WorkflowEngine()
