import json
import httpx
from typing import AsyncGenerator, Dict, Any, List
from app.llm.provider import LLMProvider
from app.config import settings

class OpenAIProvider(LLMProvider):
    def name(self) -> str:
        return "openai"

    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": kwargs.get("model", settings.LLM_MODEL),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", settings.LLM_MAX_TOKENS)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=settings.LLM_TIMEOUT_SECONDS)
            response.raise_for_status()
            return response.json()

    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": kwargs.get("model", settings.LLM_MODEL),
            "messages": messages,
            "stream": True,
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, headers=headers, json=payload, timeout=60.0) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            parsed = json.loads(data)
                            chunk = parsed["choices"][0]["delta"].get("content", "")
                            if chunk:
                                yield chunk
                        except json.JSONDecodeError:
                            pass
