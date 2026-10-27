from datetime import datetime, timezone
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


# --- Repository Knowledge Schemas ---

class ConditionDefinition(BaseModel):
    """Schema representing a condition definition loaded from the knowledge repository."""
    id: str = Field(..., description="Unique condition identifier")
    name: str = Field(..., description="Clinical condition name")
    category: str = Field(..., description="Medical category/specialty")
    icd10_code: str = Field(..., description="Associated ICD-10 diagnostic code")
    description: str = Field(..., description="Clinical overview of condition")
    primary_symptoms: List[str] = Field(default_factory=list, description="Primary hallmark symptoms")
    secondary_symptoms: List[str] = Field(default_factory=list, description="Secondary associated symptoms")
    conflicting_symptoms: List[str] = Field(default_factory=list, description="Symptoms that conflict or make condition less likely")
    risk_modifiers: Dict[str, float] = Field(default_factory=dict, description="Risk multiplier weights by patient risk key")
    references: List[str] = Field(default_factory=list, description="Medical guidelines and literature references")


class ClinicalKnowledgeBase(BaseModel):
    """Schema representing the overall repository file structure."""
    version: str
    last_updated: str
    description: str
    conditions: List[ConditionDefinition]


# --- Input Schema ---

class ClinicalInput(BaseModel):
    """Schema representing patient clinical presentation passed into the reasoning engine."""
    symptoms: List[str] = Field(default_factory=list, description="Reported symptom tags")
    chief_complaint: Optional[str] = Field(default=None, description="Free text chief complaint")
    symptom_duration: Optional[str] = Field(default=None, description="Reported duration of symptoms")
    symptom_severity: Optional[int] = Field(default=None, ge=1, le=10, description="Self-reported severity scale (1-10)")
    age: Optional[int] = Field(default=None, ge=0, description="Patient age in years")
    sex: Optional[str] = Field(default=None, description="Patient biological sex")
    chronic_conditions: List[str] = Field(default_factory=list, description="Pre-existing medical conditions")
    medications: List[str] = Field(default_factory=list, description="Current patient medications")
    allergies: List[str] = Field(default_factory=list, description="Known patient allergies")


# --- Output Sub-Models ---

class ConditionMatch(BaseModel):
    """Schema representing a matched potential condition with confidence and evidence."""
    name: str = Field(..., description="Clinical condition name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Normalized confidence score [0.0, 1.0]")
    icd10_code: str = Field(..., description="ICD-10 code for reference")
    category: str = Field(..., description="Medical category")
    supporting_symptoms: List[str] = Field(default_factory=list, description="Symptoms supporting this condition")
    conflicting_symptoms: List[str] = Field(default_factory=list, description="Present symptoms contradicting this condition")
    base_score: float = Field(..., description="Raw symptom match score before risk adjustment")
    risk_score_modifier: float = Field(..., description="Additive modifier from demographic & chronic risk factors")
    references: List[str] = Field(default_factory=list, description="Medical references supporting explainability")


class RiskFactor(BaseModel):
    """Schema representing a demographic or clinical risk factor adjustment."""
    factor_name: str = Field(..., description="Name of the risk factor (e.g. Diabetes, Age >= 65)")
    description: str = Field(..., description="Clinical rationale for risk adjustment")
    risk_weight: float = Field(..., description="Risk multiplier or modifier weight")
    affected_condition: Optional[str] = Field(default=None, description="Condition affected by this risk factor")


class MissingInformation(BaseModel):
    """Schema representing missing patient input data and its clinical impact."""
    field_name: str = Field(..., description="Input field that was missing")
    clinical_relevance: str = Field(..., description="Why this field is clinically significant")
    impact_on_reasoning: str = Field(..., description="How missing this field influenced confidence bounds")


class ReasoningStep(BaseModel):
    """Schema representing a single step in the transparent reasoning audit trace."""
    step_number: int = Field(..., description="Sequential step number")
    phase: str = Field(..., description="Pipeline phase (e.g. CONDITION_MATCHING, RISK_EVALUATION)")
    description: str = Field(..., description="Explanation of action taken in this step")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence or variables evaluated")


# --- Main Output Schema ---

class ClinicalReasoningOutput(BaseModel):
    """Complete output produced by the Clinical Reasoning Engine."""
    possible_conditions: List[ConditionMatch] = Field(default_factory=list, description="List of matched conditions ordered by confidence")
    risk_factors: List[RiskFactor] = Field(default_factory=list, description="Identified risk factors and their weights")
    missing_information: List[MissingInformation] = Field(default_factory=list, description="Missing clinical parameters")
    reasoning_steps: List[ReasoningStep] = Field(default_factory=list, description="Step-by-step audit trace of reasoning")
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of evaluation")
