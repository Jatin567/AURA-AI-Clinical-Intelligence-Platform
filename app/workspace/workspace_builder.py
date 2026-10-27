from typing import List, Optional
from datetime import datetime, timezone

from app.patients.models import PatientProfile
from app.reporting.models import ClinicalReport
from app.explanation.models import ClinicalExplanation
from app.timeline.models import TimelineEntry, TimelineSummary

from app.workspace.models import Workspace, WorkspaceMetadata, WorkspaceActions
from app.workspace.patient_adapter import PatientAdapter
from app.workspace.timeline_adapter import TimelineAdapter
from app.workspace.report_adapter import ReportAdapter
from app.workspace.trend_adapter import TrendAdapter
from app.workspace.summary_builder import SummaryBuilder

class WorkspaceBuilder:
    """Orchestrates the construction of the Workspace model."""
    
    @staticmethod
    def build(
        patient_id: str,
        profile: PatientProfile,
        current_report: ClinicalReport,
        current_explanation: ClinicalExplanation,
        historical_entries: List[TimelineEntry],
        timeline_summary: Optional[TimelineSummary]
    ) -> Workspace:
        
        # Build Metadata
        metadata = WorkspaceMetadata(
            patient_id=patient_id,
            current_assessment_id=current_report.metadata.assessment_id,
            data_sources=["patients", "timeline", "reporting", "explanation"]
        )

        # Build Adapters
        patient_summary = PatientAdapter.adapt(profile)
        timeline = TimelineAdapter.adapt(historical_entries)
        assessment_summary, reports = ReportAdapter.adapt(current_report, historical_entries)
        trends = TrendAdapter.adapt(timeline_summary)
        clinical_explanation = SummaryBuilder.adapt(current_explanation)

        return Workspace(
            metadata=metadata,
            patient=patient_summary,
            current_assessment=assessment_summary,
            timeline=timeline,
            trends=trends,
            clinical_explanation=clinical_explanation,
            reports=reports,
            actions=WorkspaceActions() # Defaults to all false
        )
