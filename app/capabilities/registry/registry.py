from typing import Dict, Optional
from app.capabilities.core.interfaces import ICapability

class CapabilityRegistry:
    def __init__(self):
        self._capabilities: Dict[str, ICapability] = {}

    def register(self, capability: ICapability):
        meta = capability.get_metadata()
        self._capabilities[meta.name] = capability

    def get_capability(self, name: str) -> Optional[ICapability]:
        return self._capabilities.get(name)
