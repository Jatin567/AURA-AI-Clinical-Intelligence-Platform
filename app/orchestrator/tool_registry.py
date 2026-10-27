from abc import ABC, abstractmethod
from typing import Dict, Any, List

class ITool(ABC):
    @abstractmethod
    def supports(self, intent: str) -> bool:
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def schema(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        pass

class ToolRegistry:
    def __init__(self):
        self._tools: List[ITool] = []

    def register(self, tool: ITool):
        self._tools.append(tool)

    def get_tools_for_intent(self, intent: str) -> List[ITool]:
        return [t for t in self._tools if t.supports(intent)]
