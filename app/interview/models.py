from enum import Enum
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from app.reasoning.models import ClinicalReasoningOutput


class EvidenceSource(str, Enum):
    """Source of clinical evidence observations."""
    PATIENT_INTERVIEW = "PATIENT_INTERVIEW"
    CLINICAL_INTAKE = "CLINICAL_INTAKE"
    DOCUMENT_OCR = "DOCUMENT_OCR"
    VOICE_TRANSCRIPT = "VOICE_TRANSCRIPT"
    IMAGING_REPORT = "IMAGING_REPORT"
    LAB_RESULT = "LAB_RESULT"
    NLU = "NLU"


class ClinicalEvidence(BaseModel):
    """Structured clinical evidence item representing a single observation."""
    evidence_id: str = Field(..., description="Unique evidence observation ID")
    source: EvidenceSource = Field(..., description="Source system/channel providing this evidence")
    key: str = Field(..., description="Standardized clinical observation key (e.g., chest_pain_radiation)")
    value: Any = Field(..., description="Structured observation value (e.g. 'yes', 'left_arm', 8)")
    clinical_tags: List[str] = Field(default_factory=list, description="Symptom tags mapped into ClinicalInput")
    confidence_weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence/reliability weight of source")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Observation timestamp")


class PriorityTier(str, Enum):
    """Clinical priority tier for dynamic question selection."""
    CRITICAL_RED_FLAG = "CRITICAL_RED_FLAG"
    DIFFERENTIAL_DISCRIMINATOR = "DIFFERENTIAL_DISCRIMINATOR"
    MISSING_DATA_RECOVERY = "MISSING_DATA_RECOVERY"
    SYMPTOM_REFINEMENT = "SYMPTOM_REFINEMENT"


class AdaptiveQuestion(BaseModel):
    """Schema representing an evidence-driven adaptive question."""
    question_id: str = Field(..., description="Unique question identifier")
    text: str = Field(..., description="Patient-facing question prompt text")
    input_type: str = Field(..., description="Input UI control type ('yes_no', 'single_select', 'number')")
    options: Optional[List[str]] = Field(default=None, description="Selectable options if input_type is select")
    purpose: str = Field(..., description="Clinical intent explaining WHY this question is asked")
    target_evidence_key: str = Field(..., description="Observation key produced when answered")
    target_condition_ids: List[str] = Field(default_factory=list, description="Conditions this question discriminates")
    evidence_mapping: Dict[str, List[str]] = Field(default_factory=dict, description="Maps option value to symptom tags")
    priority_tier: PriorityTier = Field(..., description="Clinical priority tier")
    base_information_gain: float = Field(..., ge=0.0, le=1.0, description="Base expected information gain score")


class QuestionBankSchema(BaseModel):
    """Schema representing the full question bank repository."""
    version: str
    description: str
    questions: List[AdaptiveQuestion]


class InterviewState(BaseModel):
    """State tracking an ongoing adaptive interview session."""
    session_id: str = Field(..., description="Session identifier")
    gathered_evidence: List[ClinicalEvidence] = Field(default_factory=list, description="Chronological evidence stream")
    asked_question_ids: List[str] = Field(default_factory=list, description="List of question IDs asked")
    turn_count: int = Field(default=0, ge=0, description="Number of dynamic turns executed")
    is_complete: bool = Field(default=False, description="Whether the interview loop is complete")
    completion_reason: Optional[str] = Field(default=None, description="Reason for interview termination")


class AdaptiveSelectionResult(BaseModel):
    """Result of adaptive question selection execution."""
    selected_question: Optional[AdaptiveQuestion] = Field(default=None, description="Selected question or None if complete")
    selection_rationale: str = Field(..., description="Clinical explanation of why this question was selected")
    expected_information_gain: float = Field(..., description="Calculated expected entropy reduction score")
    differential_entropy: float = Field(..., description="Current Shannon differential entropy of reasoning output")
    is_complete: bool = Field(..., description="Whether interview stopping criteria have been met")
    completion_reason: Optional[str] = Field(default=None, description="Rationale if interview completed")
    current_reasoning_output: ClinicalReasoningOutput = Field(..., description="Updated reasoning engine output after evidence")
