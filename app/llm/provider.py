from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List

class LLMProvider(ABC):
    """Abstract base class for all LLM integrations."""

    @abstractmethod
    def name(self) -> str:
        """Returns the provider name (e.g., 'openai')."""
        pass

    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Synchronously generates a response."""
        pass

    @abstractmethod
    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Asynchronously streams a response."""
        pass
