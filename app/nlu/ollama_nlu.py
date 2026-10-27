import json
import logging
import httpx
from pydantic import BaseModel, Field
from typing import List, Optional

logger = logging.getLogger(__name__)

class ClinicalEntities(BaseModel):
    chief_complaint: str = Field(default="", description="The primary reason for the patient's visit.")
    symptoms: List[str] = Field(default_factory=list, description="A list of specific medical symptoms extracted from the text.")
    duration: str = Field(default="", description="The duration of the symptoms if mentioned.")
    severity: Optional[int] = Field(default=None, description="A severity score from 1 to 10 if explicitly mentioned.")

class OllamaNLUProvider:
    def __init__(self, api_key: Optional[str] = None):
        from app.config import settings
        self.api_key = api_key or getattr(settings, "LLM_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = getattr(settings, "LLM_MODEL", "nvidia/nemotron-3.5-lightning:free") 
        
    async def extract_entities_async(self, text: str) -> ClinicalEntities:
        schema_json = ClinicalEntities.schema_json()
        
        system_prompt = (
            "You are a clinical NLU engine. Your sole purpose is to extract clinical facts from the user's message. "
            "You MUST output valid JSON that strictly conforms to the following schema:\n"
            f"{schema_json}\n\n"
            "Do NOT include any explanations, greetings, or conversational text. Output ONLY the JSON."
        )
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "AURA NLU"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                parsed_json = json.loads(content)
                return ClinicalEntities(**parsed_json)
                
        except Exception as e:
            logger.error(f"NLU Extraction failed: {e}")
            # Fallback to an empty ClinicalEntities if it fails so the pipeline can still process the raw string
            return ClinicalEntities(chief_complaint=text, symptoms=[])
