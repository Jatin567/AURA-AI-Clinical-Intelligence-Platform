from typing import List, Optional
from datetime import datetime
from app.reporting.models import ClinicalReport
from app.timeline.models import TimelineEntry, TrendAnalysisResult, TimelineSummary
from app.timeline.timeline_repository import TimelineRepository
from app.timeline.trend_analyzer import TrendAnalyzer
from app.timeline.timeline_summary import TimelineSummaryGenerator

class TimelineEngine:
    """
    Main entry point for the Patient Timeline Subsystem.
    Provides methods to add assessments and retrieve patient timelines, trend analyses, and summaries.
    """

    def __init__(self, repository: TimelineRepository):
        self._repository = repository

    def add_assessment(self, patient_id: str, report: ClinicalReport) -> None:
        """
        Translates a ClinicalReport into a TimelineEntry and saves it.
        """
        # Extract data from the report
        chief_complaint = report.patient_summary.chief_complaint
        
        # We can extract symptoms from evidence_summary or patient_summary if they were explicitly there,
        # but report structure might not have a direct "symptoms" list at root. Let's look at report structure.
        # Actually, let's just get them from evidence if available, or just use what we can.
        # For this subsystem to be robust, we'll try to find symptoms from evidence keys.
        symptoms = []
        for ev in report.evidence_summary:
            if "symptom" in ev.key.lower() or ev.key:
                # Simplistic extraction for demonstration
                symptoms.append(ev.key)
        
        top_condition = None
        top_confidence = None
        if report.clinical_reasoning_summary.leading_condition:
            top_condition = report.clinical_reasoning_summary.leading_condition
            top_confidence = report.clinical_reasoning_summary.confidence

        possible_conds = [pc.condition_name for pc in report.possible_conditions]
        
        recommendation = None
        if report.recommendations:
            recommendation = report.recommendations[0].title

        entry = TimelineEntry(
            assessment_id=report.metadata.assessment_id,
            patient_id=patient_id,
            timestamp=report.metadata.generation_timestamp,
            chief_complaint=chief_complaint,
            symptoms=symptoms,
            severity=report.severity,
            top_condition=top_condition,
            top_confidence=top_confidence,
            possible_conditions=possible_conds,
            recommendation=recommendation,
            report_reference=report
        )
        self._repository.add_entry(entry)

    def get_patient_timeline(self, patient_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[TimelineEntry]:
        """
        Retrieves the chronologically sorted timeline for a patient.
        """
        return self._repository.get_patient_timeline(patient_id, start_date, end_date)

    def get_timeline(self, patient_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[TimelineEntry]:
        """
        Convenience alias for get_patient_timeline.
        """
        return self.get_patient_timeline(patient_id, start_date, end_date)

    def analyze_trends(self, patient_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> TrendAnalysisResult:
        """
        Performs deterministic trend analysis on the patient's timeline history.
        """
        history = self.get_patient_timeline(patient_id, start_date, end_date)
        return TrendAnalyzer.analyze(history)

    def generate_summary(self, patient_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> TimelineSummary:
        """
        Generates a structured longitudinal summary of the patient's timeline.
        """
        trends = self.analyze_trends(patient_id, start_date, end_date)
        return TimelineSummaryGenerator.generate(trends)
