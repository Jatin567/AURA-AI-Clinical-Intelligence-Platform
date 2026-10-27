from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExecutiveSummary(BaseModel):
    """Top-line patient-safe summary of deterministic reasoning output."""

    leading_condition: Optional[str] = None
    summary: str
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    diagnosis_notice: str


class ConditionExplanation(BaseModel):
    """Readable explanation for a possible condition from the reasoning engine."""

    condition_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    confidence_percent: int = Field(..., ge=0, le=100)
    supporting_findings: List[str] = Field(default_factory=list)
    conflicting_findings: List[str] = Field(default_factory=list)
    explanation: str


class RiskExplanation(BaseModel):
    """Readable explanation of a deterministic risk factor."""

    factor_name: str
    description: str
    risk_weight: float
    affected_condition: Optional[str] = None
    explanation: str


class Recommendation(BaseModel):
    """Deterministic recommendation derived from authoritative severity."""

    severity: str
    title: str
    action: str
    timeframe: str
    rationale: str
    priority: int = Field(..., ge=1)


class SafetyNotice(BaseModel):
    """Safety notice generated from severity or deterministic red flag context."""

    severity: str
    title: str
    message: str
    immediate_action_required: bool = False


class Disclaimer(BaseModel):
    """Mandatory clinical disclaimer."""

    informational_only: str
    not_a_diagnosis: str
    seek_professional_care: str


class ClinicalExplanation(BaseModel):
    """Complete deterministic clinical explanation for future reports."""

    executive_summary: ExecutiveSummary
    possible_conditions: List[ConditionExplanation] = Field(default_factory=list)
    risk_factors: List[RiskExplanation] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    safety_notices: List[SafetyNotice] = Field(default_factory=list)
    disclaimer: Disclaimer
    source: str = "deterministic_clinical_reasoning"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_structured_json(self) -> Dict[str, Any]:
        """Return a JSON-serializable dictionary."""
        return self.model_dump(mode="json")

