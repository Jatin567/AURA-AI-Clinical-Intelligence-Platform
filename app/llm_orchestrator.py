import asyncio
import json
import httpx
from datetime import datetime, timezone
from typing import Optional
from app.config import settings
from app.models.session import SessionState
from app.models.triage import TriageDecision, TriageLevel
from app.models.llm import LLMResponse, OrchestratorResult

class LLMOrchestrator:
    """
    Orchestrates LLM calls to generate natural language explanations for triage decisions.
    Strictly follows architectural constraints: LLM never overrides triage_level.
    """

    SYSTEM_PROMPT_TEMPLATE = """You are a medical triage assistant. Be clear, calm, and empathetic.
Never diagnose. Never prescribe. Never contradict the triage level you have been given.
The triage level is {triage_level} — do not suggest it could be lower.
If suggesting OTC medicines, only suggest common, widely available options. Format them in a section starting with OTC_CANDIDATES: followed by a comma-separated list.
Always end your response with a medical disclaimer.
Respond in plain English suitable for a general adult audience.

The primary reason for this classification is: {primary_reason}"""

    async def generate_explanation(self, session: SessionState, triage: TriageDecision) -> OrchestratorResult:
        """
        Generates an LLM-based explanation for the triage decision.
        Skips LLM for EMERGENCY cases.
        """
        now = datetime.now(timezone.utc)

        # 1. Skip logic for EMERGENCY
        if triage.triage_level == TriageLevel.EMERGENCY:
            return OrchestratorResult(
                session_id=session.session_id,
                triage_decision=triage,
                llm_response=None,
                assembled_at=now,
                llm_skipped=True,
                skip_reason="Emergency triage — immediate action required, LLM explanation suppressed"
            )

        try:
            # 2. Construct Prompts
            system_prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
                triage_level=triage.triage_level.value,
                primary_reason=triage.primary_reason
            )
            user_prompt = self._construct_user_prompt(session, triage)

            # 3. Call LLM with timeout
            llm_payload = {
                "model": settings.LLM_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": settings.LLM_MAX_TOKENS,
                "temperature": 0.7
            }

            response = await asyncio.wait_for(
                self._call_llm_api(llm_payload),
                timeout=settings.LLM_TIMEOUT_SECONDS
            )

            # 4. Parse Response
            parsed_response = self._parse_llm_output(response)
            
            return OrchestratorResult(
                session_id=session.session_id,
                triage_decision=triage,
                llm_response=parsed_response,
                assembled_at=now
            )

        except asyncio.TimeoutError:
            return self._build_error_result(session, triage, "LLM request timed out", now)
        except Exception as e:
            return self._build_error_result(session, triage, str(e), now)

    def _construct_user_prompt(self, session: SessionState, triage: TriageDecision) -> str:
        """Constructs the user prompt without internal IDs or full history."""
        # Demographics
        profile = session.patient_profile
        age_str = str(profile.age) if profile and profile.age is not None else "Unknown"
        sex_str = profile.sex if profile and profile.sex else "Unknown"
        
        # Symptoms
        cc = session.chief_complaint or "None"
        duration = session.symptom_duration or "Unknown"
        severity = str(session.symptom_severity) if session.symptom_severity is not None else "Unknown"
        associated = ", ".join(session.symptoms) if session.symptoms else "None"
        
        # Conditions
        conditions = ", ".join(profile.known_conditions) if profile and profile.known_conditions else "None"

        # History: Last 10 turns
        history = list(session.conversation_history)[-10:] if session.conversation_history else []
        history_str = "\n".join([f"Q: {h['question_text']}\nA: {h['answer']}" for h in history])

        prompt = f"""Patient Profile: {age_str} year old {sex_str}
Chief Complaint: {cc}
Symptom Duration: {duration}
Severity Score: {severity}/10
Associated Symptoms: {associated}
Known Conditions: {conditions}

Triage Level: {triage.triage_level.value}
Primary Reason: {triage.primary_reason}

Conversation History (Last 10 turns):
{history_str}
"""
        return prompt

    async def _call_llm_api(self, payload: dict) -> dict:
        """Routes the LLM call to the correct provider API."""
        provider = settings.LLM_PROVIDER.lower()
        if provider == "gemini":
            return await self._call_gemini(payload)
        elif provider == "ollama":
            return await self._call_ollama(payload)
        else:
            return await self._call_openai(payload)

    async def _call_ollama(self, payload: dict) -> dict:
        """Calls the Ollama /api/chat endpoint for local inference."""
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"

        # Ollama expects: {model, messages, stream, options}
        ollama_payload = {
            "model": settings.LLM_MODEL,
            "messages": payload["messages"],
            "stream": False,
            "options": {
                "num_predict": payload.get("max_tokens", 800),
                "temperature": payload.get("temperature", 0.7)
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=ollama_payload,
                timeout=settings.LLM_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            data = response.json()

        # Normalize to OpenAI shape
        return {
            "choices": [{
                "message": {
                    "content": data.get("message", {}).get("content", "")
                }
            }],
            "model": data.get("model", settings.LLM_MODEL),
            "usage": {
                "prompt_tokens": data.get("prompt_eval_count"),
                "completion_tokens": data.get("eval_count")
            }
        }

    async def _call_openai(self, payload: dict) -> dict:
        """Calls the OpenAI chat completions endpoint."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=settings.LLM_TIMEOUT_SECONDS)
            response.raise_for_status()
            return response.json()

    async def _call_gemini(self, payload: dict) -> dict:
        """Calls the Google Gemini generateContent endpoint and normalises the
        response into OpenAI-compatible shape so the rest of the pipeline
        doesn't need to change."""
        model = settings.LLM_MODEL  # e.g. "gemini-1.5-flash"
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={settings.LLM_API_KEY}"
        )

        # Build Gemini request body from OpenAI-style messages
        system_parts = []
        user_parts = []
        for msg in payload["messages"]:
            if msg["role"] == "system":
                system_parts.append({"text": msg["content"]})
            else:
                user_parts.append({"text": msg["content"]})

        gemini_payload = {
            "systemInstruction": {"parts": system_parts} if system_parts else None,
            "contents": [{"role": "user", "parts": user_parts}],
            "generationConfig": {
                "maxOutputTokens": payload.get("max_tokens", 800),
                "temperature": payload.get("temperature", 0.7)
            }
        }
        # Remove None keys
        gemini_payload = {k: v for k, v in gemini_payload.items() if v is not None}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=gemini_payload, timeout=settings.LLM_TIMEOUT_SECONDS)
            response.raise_for_status()
            data = response.json()

        # Normalise to OpenAI shape
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata", {})
        return {
            "choices": [{"message": {"content": text}}],
            "model": model,
            "usage": {
                "prompt_tokens": usage.get("promptTokenCount"),
                "completion_tokens": usage.get("candidatesTokenCount")
            }
        }

    def _parse_llm_output(self, response_data: dict) -> LLMResponse:
        """Parses the raw JSON response from the LLM."""
        raw_text = response_data['choices'][0]['message']['content']
        
        # Extract OTC_CANDIDATES
        explanation = raw_text
        otc_candidates = []
        
        if "OTC_CANDIDATES:" in raw_text:
            parts = raw_text.split("OTC_CANDIDATES:")
            explanation = parts[0].strip()
            # Handle potential lines or formatting after OTC_CANDIDATES
            candidate_line = parts[1].split("\n")[0].strip()
            otc_candidates = [c.strip() for c in candidate_line.split(",") if c.strip()]
            
            # Re-assemble explanation if there's text after the OTC line
            remaining = "\n".join(parts[1].split("\n")[1:])
            if remaining.strip():
                explanation += "\n" + remaining.strip()

        return LLMResponse(
            explanation=explanation,
            suggested_questions=[], # LLM can suggest these in explanation or we can add extraction
            otc_candidates=otc_candidates,
            raw_response=raw_text,
            model_used=response_data.get('model', settings.LLM_MODEL),
            prompt_tokens=response_data.get('usage', {}).get('prompt_tokens'),
            completion_tokens=response_data.get('usage', {}).get('completion_tokens')
        )

    def _build_error_result(self, session: SessionState, triage: TriageDecision, 
                            error_msg: str, now: datetime) -> OrchestratorResult:
        """Builds a result with a safe fallback explanation on LLM failure."""
        fallback_explanation = (
            "Based on your symptoms, we've provided a triage recommendation. "
            "Our automated detailed explanation service is currently experiencing a delay, "
            "but please follow the instructions for the assigned triage level above."
        )
        
        return OrchestratorResult(
            session_id=session.session_id,
            triage_decision=triage,
            llm_response=LLMResponse(
                explanation=fallback_explanation,
                suggested_questions=[],
                otc_candidates=[],
                raw_response="",
                model_used=settings.LLM_MODEL,
                generation_error=error_msg
            ),
            assembled_at=now
        )
