import json
import logging
import httpx
from typing import AsyncGenerator, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class StreamingLLMProvider:
    def __init__(self, provider_name: str = None):
        self.provider_name = (provider_name or settings.LLM_PROVIDER or "openrouter").lower()
        
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        if self.provider_name == "ollama":
            async for chunk in self._stream_ollama(prompt):
                yield chunk
        elif self.provider_name == "gemini":
            async for chunk in self._stream_gemini(prompt):
                yield chunk
        else:
            # Default to OpenRouter / Nemotron
            async for chunk in self._stream_openrouter(prompt):
                yield chunk

    async def _stream_ollama(self, prompt: str) -> AsyncGenerator[str, None]:
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": settings.LLM_MODEL,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.7
            }
        }
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, timeout=60.0) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except json.JSONDecodeError:
                            continue

    async def _stream_gemini(self, prompt: str) -> AsyncGenerator[str, None]:
        model = settings.LLM_MODEL if "gemini" in settings.LLM_MODEL else "gemini-3.8-flash"
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:streamGenerateContent?alt=sse&key={settings.LLM_API_KEY}"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7
            }
        }
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, timeout=60.0) as response:
                if response.status_code != 200:
                    logger.warning(f"Gemini streaming status {response.status_code}, falling back to OpenRouter")
                    async for chunk in self._stream_openrouter(prompt):
                        yield chunk
                    return
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if "candidates" in data and len(data["candidates"]) > 0:
                                parts = data["candidates"][0].get("content", {}).get("parts", [])
                                if parts:
                                    yield parts[0].get("text", "")
                        except json.JSONDecodeError:
                            continue

    async def _stream_openrouter(self, prompt: str, model: str = None) -> AsyncGenerator[str, None]:
        target_model = model or settings.LLM_MODEL or "nvidia/nemotron-3-ultra-550b-a55b:free"
        url = "https://openrouter.ai/api/v1/chat/completions"
        api_key = settings.LLM_API_KEY
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "AURA"
        }
        payload = {
            "model": target_model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
            "temperature": 0.7
        }
        
        fallback_models = ["nvidia/nemotron-3.5-lightning:free", "openrouter/free"]

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", url, headers=headers, json=payload, timeout=45.0) as response:
                    if response.status_code != 200:
                        logger.warning(f"OpenRouter model {target_model} returned {response.status_code}. Attempting fallback...")
                        raise httpx.HTTPStatusError(f"HTTP {response.status_code}", request=response.request, response=response)

                    has_yielded = False
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        has_yielded = True
                                        yield content
                            except json.JSONDecodeError:
                                continue
                    if has_yielded:
                        return
        except Exception as e:
            logger.error(f"Stream error with model {target_model}: {e}")
            if target_model != fallback_models[0]:
                logger.info(f"Retrying with fallback model {fallback_models[0]}")
                async for chunk in self._stream_openrouter(prompt, model=fallback_models[0]):
                    yield chunk
            else:
                yield "I am experiencing high demand at the moment. Please consult a qualified healthcare provider for immediate medical guidance."
