from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from app.models.red_flag import RedFlagResult


class TriageLevel(str, Enum):
    EMERGENCY = "EMERGENCY"
    URGENT = "URGENT"
    ROUTINE = "ROUTINE"
    HOME_CARE = "HOME_CARE"


class TriageDecision(BaseModel):
    session_id: str
    triage_level: TriageLevel
    confidence: Literal["high", "medium", "low"]
    primary_reason: str
    contributing_factors: List[str] = Field(default_factory=list)
    red_flag_result: RedFlagResult
    classified_at: datetime
    classification_version: str = "1.0"
