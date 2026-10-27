import json
from app.reporting.models import ClinicalReport
from app.reporting.renderers.base import ReportRenderer


class JSONRenderer(ReportRenderer):
    """
    Renders the clinical report as a JSON string.
    """
    def render(self, report: ClinicalReport) -> str:
        # Pydantic's model_dump_json handles serialization of datetime and enums
        return report.model_dump_json(indent=2)
