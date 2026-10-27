from typing import List
from app.orchestrator.tool_registry import ToolRegistry, ITool

class ToolPlanner:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def plan_tools(self, intent: str) -> List[ITool]:
        """Dynamically select required tools based on intent."""
        # Query the registry for matching tools
        selected = self.registry.get_tools_for_intent(intent)
        return selected
