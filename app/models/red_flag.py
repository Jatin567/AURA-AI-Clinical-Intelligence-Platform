from datetime import datetime
from enum import Enum
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class RedFlagSeverity(str, Enum):
    EMERGENCY = "EMERGENCY"
    URGENT = "URGENT"


class RedFlagMatch(BaseModel):
    rule_id: str
    severity: RedFlagSeverity
    matched_on: str
    explanation: str
    rule_description: str
    requires_immediate_crisis_resource: bool = False


class RedFlagResult(BaseModel):
    evaluated_at: datetime
    flags_matched: List[RedFlagMatch] = Field(default_factory=list)
    highest_severity: Optional[RedFlagSeverity] = None
    input_snapshot: dict
    evaluation_error: Optional[str] = None
