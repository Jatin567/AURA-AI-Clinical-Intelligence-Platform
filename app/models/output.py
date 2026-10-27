from datetime import datetime
from typing import List
from pydantic import BaseModel
from app.models.triage import TriageLevel

class TriageOutput(BaseModel):
    session_id: str
    triage_level: TriageLevel
    triage_label: str
    explanation: str
    approved_otc_suggestions: List[str]
    otc_disclaimers: List[str]
    action_items: List[str]
    crisis_resources: List[str]
    medical_disclaimer: str
    assembled_at: datetime
    llm_was_used: bool
