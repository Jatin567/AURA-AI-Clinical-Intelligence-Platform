from app.patients.profile_service import ProfileService
from app.timeline.timeline_engine import TimelineEngine
from app.reporting.models import ClinicalReport
from app.explanation.models import ClinicalExplanation

from app.workspace.models import Workspace
from app.workspace.workspace_builder import WorkspaceBuilder

class WorkspaceService:
    """
    High-level entry point for constructing a Workspace.
    Fetches required context from Patient and Timeline subsystems.
    """
    
    def __init__(self, profile_service: ProfileService, timeline_engine: TimelineEngine):
        self.profile_service = profile_service
        self.timeline_engine = timeline_engine

    def build_workspace(self, patient_id: str, current_report: ClinicalReport, current_explanation: ClinicalExplanation) -> Workspace:
        profile = self.profile_service.get_profile(patient_id)
        if not profile:
            raise ValueError(f"Patient profile {patient_id} not found.")

        # Safely fetch timeline, missing history returns empty lists
        historical_entries = self.timeline_engine.get_patient_timeline(patient_id) or []
        timeline_summary = None
        if historical_entries:
            timeline_summary = self.timeline_engine.generate_summary(patient_id)

        return WorkspaceBuilder.build(
            patient_id=patient_id,
            profile=profile,
            current_report=current_report,
            current_explanation=current_explanation,
            historical_entries=historical_entries,
            timeline_summary=timeline_summary
        )
