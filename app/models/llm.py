from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.triage import TriageDecision

class LLMResponse(BaseModel):
    explanation: str
    suggested_questions: List[str]
    otc_candidates: List[str] = Field(
        ..., 
        description="Raw LLM suggestions. MUST be validated by Module 6 (OTC Validator) before surfacing to users."
    )
    raw_response: str
    model_used: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    generation_error: Optional[str] = None

class OrchestratorResult(BaseModel):
    session_id: str
    triage_decision: TriageDecision
    llm_response: Optional[LLMResponse] = None
    assembled_at: datetime
    llm_skipped: bool = False
    skip_reason: Optional[str] = None
