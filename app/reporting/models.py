from datetime import datetime, timezone
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
import uuid

class AssessmentContext(BaseModel):
    """
    Input abstraction for the reporting subsystem.
    Contains strictly the context needed to generate the report.
    """
    assessment_id: Optional[str] = None
    session_id: Optional[str] = None
    chief_complaint: Optional[str] = None
    symptom_severity: Optional[int] = None
    symptom_duration: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    chronic_conditions: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    severity: str = Field(..., description="The authoritative severity / triage level (e.g. EMERGENCY, URGENT)")
    evidence_collected: List[Dict[str, Any]] = Field(default_factory=list, description="List of evidence gathered during interview")
    interview_turn_count: int = Field(default=0)
    interview_completion_reason: Optional[str] = None

    model_config = {
        "frozen": True # Immutable
    }


class ReportMetadata(BaseModel):
    assessment_id: str
    session_id: Optional[str] = None
    generation_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    aura_version: str = "1.0"
    knowledge_base_version: str = "1.0"
    reasoning_engine_version: str = "1.0"
    explanation_engine_version: str = "1.0"


class PatientSummary(BaseModel):
    chief_complaint: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    chronic_conditions: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)


class InterviewSummary(BaseModel):
    turn_count: int
    completion_reason: Optional[str] = None
    symptom_duration: Optional[str] = None
    symptom_severity: Optional[int] = None


class EvidenceItem(BaseModel):
    source: str
    key: str
    value: Any
    confidence_weight: float
    timestamp: datetime


class ReasoningSummary(BaseModel):
    leading_condition: Optional[str] = None
    confidence: Optional[float] = None
    summary: str


class PossibleCondition(BaseModel):
    condition_name: str
    confidence: float
    confidence_percent: int
    supporting_findings: List[str] = Field(default_factory=list)
    conflicting_findings: List[str] = Field(default_factory=list)
    explanation: str


class RiskFactor(BaseModel):
    factor_name: str
    description: str
    risk_weight: float
    affected_condition: Optional[str] = None
    explanation: str


class Recommendation(BaseModel):
    severity: str
    title: str
    action: str
    timeframe: str
    rationale: str
    priority: int


class SafetyNotice(BaseModel):
    severity: str
    title: str
    message: str
    immediate_action_required: bool


class ClinicalDisclaimer(BaseModel):
    informational_only: str
    not_a_diagnosis: str
    seek_professional_care: str


class AuditMetadata(BaseModel):
    reasoning_steps: List[str] = Field(default_factory=list)


class ClinicalReport(BaseModel):
    metadata: ReportMetadata
    patient_summary: PatientSummary
    interview_summary: InterviewSummary
    evidence_summary: List[EvidenceItem] = Field(default_factory=list)
    clinical_reasoning_summary: ReasoningSummary
    possible_conditions: List[PossibleCondition] = Field(default_factory=list)
    risk_factors: List[RiskFactor] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    severity: str
    recommendations: List[Recommendation] = Field(default_factory=list)
    safety_notices: List[SafetyNotice] = Field(default_factory=list)
    clinical_disclaimer: ClinicalDisclaimer
    audit_metadata: AuditMetadata
