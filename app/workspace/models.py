from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class WorkspaceMetadata(BaseModel):
    workspace_version: str = "1.0"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    patient_id: str
    current_assessment_id: Optional[str] = None
    data_sources: List[str] = Field(default_factory=list)

class WorkspacePatientSummary(BaseModel):
    full_name: str
    date_of_birth: str
    biological_sex: str
    chronic_conditions: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)

class WorkspaceAssessmentSummary(BaseModel):
    chief_complaint: Optional[str] = None
    severity: str
    top_condition: Optional[str] = None
    confidence: Optional[float] = None
    recommendations: List[str] = Field(default_factory=list)

class WorkspaceTimelineEntry(BaseModel):
    assessment_id: str
    timestamp: datetime
    chief_complaint: Optional[str] = None
    severity: str
    top_condition: Optional[str] = None

class WorkspaceTimeline(BaseModel):
    historical_assessments: List[WorkspaceTimelineEntry] = Field(default_factory=list)

class WorkspaceTrends(BaseModel):
    symptom_trends: str = ""
    severity_trends: str = ""
    condition_trends: str = ""

class WorkspaceClinicalExplanation(BaseModel):
    executive_summary: str = ""
    supporting_findings: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)

class WorkspaceReports(BaseModel):
    current_report_reference: Any = None
    historical_report_references: List[Any] = Field(default_factory=list)

class WorkspaceActions(BaseModel):
    can_export_pdf: bool = False
    can_compare_assessments: bool = False
    can_generate_fhir: bool = False
    can_share_report: bool = False

class Workspace(BaseModel):
    metadata: WorkspaceMetadata
    patient: WorkspacePatientSummary
    current_assessment: WorkspaceAssessmentSummary
    timeline: WorkspaceTimeline
    trends: WorkspaceTrends
    clinical_explanation: WorkspaceClinicalExplanation
    reports: WorkspaceReports
    actions: WorkspaceActions = Field(default_factory=WorkspaceActions)
