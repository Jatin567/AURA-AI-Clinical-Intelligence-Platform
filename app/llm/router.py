from typing import Dict
from app.llm.provider import LLMProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.stubs import GeminiProvider, OllamaProvider, ClaudeProvider, GroqProvider, OpenRouterProvider
from app.config.features import features
from app.observability.logger import logger

class ProviderRouter:
    """Intelligently routes requests to the appropriate LLM provider."""
    
    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider(),
            "ollama": OllamaProvider(),
            "claude": ClaudeProvider(),
            "groq": GroqProvider(),
            "openrouter": OpenRouterProvider()
        }
        
    def get_provider(self, requested_provider: str = None) -> LLMProvider:
        """Selects a provider based on request, fallback to defaults."""
        target = requested_provider or features.default_llm_provider
        
        provider = self._providers.get(target)
        if not provider:
            logger.log_event("PROVIDER_FALLBACK", "system", {"requested": target, "fallback": features.fallback_llm_provider})
            return self._providers[features.fallback_llm_provider]
            
        return provider

provider_router = ProviderRouter()
