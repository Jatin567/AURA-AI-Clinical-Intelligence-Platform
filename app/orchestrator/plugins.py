from abc import ABC, abstractmethod
from typing import Dict, Any, List

class PluginInterface(ABC):
    @property
    @abstractmethod
    def id(self) -> str: pass
    
    @property
    @abstractmethod
    def version(self) -> str: pass
    
    @property
    @abstractmethod
    def permissions(self) -> List[str]: pass
    
    @abstractmethod
    def supports(self, intent: str) -> bool: pass
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]: pass
    
    @abstractmethod
    def metadata(self) -> Dict[str, Any]: pass

class PluginDiscovery:
    def __init__(self):
        self.plugins: Dict[str, PluginInterface] = {}
        
    def register(self, plugin: PluginInterface):
        self.plugins[plugin.id] = plugin
        
    def get_plugins_for_intent(self, intent: str) -> List[PluginInterface]:
        return [p for p in self.plugins.values() if p.supports(intent)]

plugin_discovery = PluginDiscovery()
