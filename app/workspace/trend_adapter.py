from typing import Optional
from app.timeline.models import TimelineSummary
from app.workspace.models import WorkspaceTrends

class TrendAdapter:
    """Adapts TimelineSummary into WorkspaceTrends."""
    
    @staticmethod
    def adapt(timeline_summary: Optional[TimelineSummary]) -> WorkspaceTrends:
        if not timeline_summary:
            return WorkspaceTrends()
            
        return WorkspaceTrends(
            symptom_trends=timeline_summary.symptom_summary,
            severity_trends=timeline_summary.severity_summary,
            condition_trends=timeline_summary.condition_summary
        )
