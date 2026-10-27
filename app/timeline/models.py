from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from enum import IntEnum

class SeverityLevel(IntEnum):
    """
    Standardized severity ordering for trend analysis.
    Higher integer = higher severity.
    """
    SELF_CARE = 1
    HOME_CARE = 1 # Map HOME_CARE to SELF_CARE level
    ROUTINE = 2
    URGENT = 3
    EMERGENCY = 4

    @classmethod
    def from_string(cls, severity_str: str) -> "SeverityLevel":
        s = severity_str.upper()
        if s == "HOME_CARE":
            return cls.SELF_CARE
        try:
            return cls[s]
        except KeyError:
            return cls.ROUTINE  # default fallback

class TimelineEntry(BaseModel):
    """
    Represents a single clinical assessment in the patient's timeline.
    """
    assessment_id: str
    patient_id: str
    timestamp: datetime
    chief_complaint: Optional[str] = None
    symptoms: List[str] = Field(default_factory=list)
    severity: str
    top_condition: Optional[str] = None
    top_confidence: Optional[float] = None
    possible_conditions: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = None
    report_reference: Any = Field(default=None, description="The full ClinicalReport or reference to it")


class TrendAnalysisResult(BaseModel):
    recurring_symptoms: List[str] = Field(default_factory=list)
    newly_introduced_symptoms: List[str] = Field(default_factory=list)
    resolved_symptoms: List[str] = Field(default_factory=list)
    worsening_symptoms: List[str] = Field(default_factory=list)
    improving_symptoms: List[str] = Field(default_factory=list)
    recurring_conditions: List[str] = Field(default_factory=list)
    confidence_increases: Dict[str, float] = Field(default_factory=dict)
    confidence_decreases: Dict[str, float] = Field(default_factory=dict)
    assessment_frequency: str = ""
    severity_escalation: bool = False
    severity_de_escalation: bool = False
    severity_trend_description: str = ""


class TimelineSummary(BaseModel):
    overall_summary: str
    severity_summary: str
    symptom_summary: str
    condition_summary: str
    recommendation_summary: str
