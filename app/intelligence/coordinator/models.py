from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class ClinicalContext(BaseModel):
    """Immutable context shared by every intelligence engine."""
    patient_profile: Dict[str, Any] = Field(default_factory=dict)
    clinical_reasoning_output: Dict[str, Any] = Field(default_factory=dict)
    interview_output: Dict[str, Any] = Field(default_factory=dict)
    timeline: Dict[str, Any] = Field(default_factory=dict)
    workspace: Dict[str, Any] = Field(default_factory=dict)
    medical_history: List[Dict[str, Any]] = Field(default_factory=list)
    symptoms: List[Dict[str, Any]] = Field(default_factory=list)
    knowledge_retrieval_results: List[Dict[str, Any]] = Field(default_factory=list)
    conversation_context: Dict[str, Any] = Field(default_factory=dict)
    uploaded_documents: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        frozen = True  # Enforce immutability

class ConfidenceMetrics(BaseModel):
    clinical_confidence: float = 0.0
    evidence_confidence: float = 0.0
    knowledge_confidence: float = 0.0
    recommendation_confidence: float = 0.0
    overall_confidence: float = 0.0
    missing_information_penalty: float = 0.0

class ClinicalDecisionTrace(BaseModel):
    """Complete audit trail for a clinical decision."""
    session_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reasoning_output: Dict[str, Any] = Field(default_factory=dict)
    knowledge_retrieved: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_used: List[Dict[str, Any]] = Field(default_factory=list)
    risk_assessment: Dict[str, Any] = Field(default_factory=dict)
    drug_safety_analysis: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: ConfidenceMetrics = Field(default_factory=ConfidenceMetrics)
    final_ui_blocks: List[Dict[str, Any]] = Field(default_factory=list)
