from typing import List
from app.timeline.models import TimelineEntry
from app.workspace.models import WorkspaceTimeline, WorkspaceTimelineEntry

class TimelineAdapter:
    """Adapts a list of TimelineEntry objects into a WorkspaceTimeline."""
    
    @staticmethod
    def adapt(entries: List[TimelineEntry]) -> WorkspaceTimeline:
        workspace_entries = []
        for entry in entries:
            workspace_entries.append(WorkspaceTimelineEntry(
                assessment_id=entry.assessment_id,
                timestamp=entry.timestamp,
                chief_complaint=entry.chief_complaint,
                severity=entry.severity,
                top_condition=entry.top_condition
            ))
        return WorkspaceTimeline(historical_assessments=workspace_entries)
