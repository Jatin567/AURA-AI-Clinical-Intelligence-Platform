from typing import List, Optional
from pydantic import BaseModel

class ProviderConfig(BaseModel):
    name: str
    latency_ms: float = 0.0
    cost_per_1k: float = 0.0
    available: bool = True
    capabilities: List[str] = []

class ProviderSelectionPolicy:
    def select_best(self, providers: List[ProviderConfig], required_caps: List[str]) -> Optional[ProviderConfig]:
        valid = [p for p in providers if p.available and all(c in p.capabilities for c in required_caps)]
        
        if not valid:
            return None
            
        # Example policy: sort by latency then cost
        valid.sort(key=lambda x: (x.latency_ms, x.cost_per_1k))
        return valid[0]
