from typing import List, Optional, Any
from app.orchestrator.provider_policy import ProviderSelectionPolicy, ProviderConfig

class ProviderRouter:
    def __init__(self, policy: ProviderSelectionPolicy):
        self.policy = policy
        self.providers: List[ProviderConfig] = [
            ProviderConfig(name="gemini", capabilities=["tools", "vision"]),
            ProviderConfig(name="openai", capabilities=["tools", "json"]),
            ProviderConfig(name="ollama", capabilities=["local"])
        ]

    def route_request(self, required_caps: List[str]) -> Optional[str]:
        best = self.policy.select_best(self.providers, required_caps)
        if best:
            return best.name
        return None
