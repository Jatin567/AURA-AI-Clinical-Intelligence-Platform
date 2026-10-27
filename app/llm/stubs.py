from typing import AsyncGenerator, Dict, Any, List
from app.llm.provider import LLMProvider

class GeminiProvider(LLMProvider):
    def name(self) -> str: return "gemini"
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        return {"choices": [{"message": {"content": "Gemini generation stub"}}]}
    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        yield "Gemini stream stub"

class OllamaProvider(LLMProvider):
    def name(self) -> str: return "ollama"
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        return {"choices": [{"message": {"content": "Ollama generation stub"}}]}
    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        yield "Ollama stream stub"

class ClaudeProvider(LLMProvider):
    def name(self) -> str: return "claude"
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]: pass
    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]: pass

class GroqProvider(LLMProvider):
    def name(self) -> str: return "groq"
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]: pass
    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]: pass

class OpenRouterProvider(LLMProvider):
    def name(self) -> str: return "openrouter"
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]: pass
    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]: pass
