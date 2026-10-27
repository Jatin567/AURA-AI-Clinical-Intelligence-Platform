from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.models.triage import TriageLevel

class OTCMedicine(BaseModel):
    name: str
    common_names: List[str]
    safe_for_ages_above: int  # minimum age in years
    contraindicated_conditions: List[str]
    contraindicated_medications: List[str]
    max_duration_days: int
    standard_disclaimer: str

class OTCSuggestion(BaseModel):
    medicine: OTCMedicine
    approved: bool
    rejection_reason: Optional[str] = None

class OTCResult(BaseModel):
    session_id: str
    suggestions: List[OTCSuggestion]
    evaluated_at: datetime
    triage_level_at_evaluation: TriageLevel
    rejection_reason: Optional[str] = None
