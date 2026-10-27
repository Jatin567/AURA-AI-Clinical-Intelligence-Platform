from typing import List, Tuple, Any
from app.reporting.models import ClinicalReport
from app.workspace.models import WorkspaceAssessmentSummary, WorkspaceReports
from app.timeline.models import TimelineEntry

class ReportAdapter:
    """Adapts ClinicalReport and Timeline history into Workspace Assessment and Reports models."""
    
    @staticmethod
    def adapt(current_report: ClinicalReport, historical_entries: List[TimelineEntry]) -> Tuple[WorkspaceAssessmentSummary, WorkspaceReports]:
        # Build Assessment Summary
        recommendations = [r.title for r in current_report.recommendations] if current_report.recommendations else []
        
        top_condition = None
        confidence = None
        if current_report.clinical_reasoning_summary.leading_condition:
            top_condition = current_report.clinical_reasoning_summary.leading_condition
            confidence = current_report.clinical_reasoning_summary.confidence

        assessment_summary = WorkspaceAssessmentSummary(
            chief_complaint=current_report.patient_summary.chief_complaint,
            severity=current_report.severity,
            top_condition=top_condition,
            confidence=confidence,
            recommendations=recommendations
        )

        # Build Reports Summary
        historical_reports = []
        for entry in historical_entries:
            if entry.report_reference:
                historical_reports.append(entry.report_reference)

        reports = WorkspaceReports(
            current_report_reference=current_report,
            historical_report_references=historical_reports
        )

        return assessment_summary, reports
