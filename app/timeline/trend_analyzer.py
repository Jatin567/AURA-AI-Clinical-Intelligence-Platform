from typing import List
from app.timeline.models import TimelineEntry, TrendAnalysisResult
from app.timeline.analyzers import (
    SymptomTrendAnalyzer, SeverityTrendAnalyzer, 
    ConditionTrendAnalyzer, ConfidenceTrendAnalyzer
)

class TrendAnalyzer:
    """
    Orchestrates deterministic trend analysis across a patient's assessment history.
    """

    @classmethod
    def analyze(cls, history: List[TimelineEntry]) -> TrendAnalysisResult:
        if not history:
            return TrendAnalysisResult()

        symptom_data = SymptomTrendAnalyzer.analyze(history)
        severity_data = SeverityTrendAnalyzer.analyze(history)
        condition_data = ConditionTrendAnalyzer.analyze(history)
        confidence_data = ConfidenceTrendAnalyzer.analyze(history)

        # Assessment frequency
        freq_desc = f"{len(history)} assessments recorded."
        if len(history) > 1:
            days_diff = (history[-1].timestamp - history[0].timestamp).days
            freq_desc = f"{len(history)} assessments recorded over {days_diff} days."

        return TrendAnalysisResult(
            recurring_symptoms=symptom_data.get("recurring_symptoms", []),
            newly_introduced_symptoms=symptom_data.get("newly_introduced_symptoms", []),
            resolved_symptoms=symptom_data.get("resolved_symptoms", []),
            worsening_symptoms=symptom_data.get("worsening_symptoms", []),
            improving_symptoms=symptom_data.get("improving_symptoms", []),
            recurring_conditions=condition_data.get("recurring_conditions", []),
            confidence_increases=confidence_data.get("confidence_increases", {}),
            confidence_decreases=confidence_data.get("confidence_decreases", {}),
            assessment_frequency=freq_desc,
            severity_escalation=severity_data.get("severity_escalation", False),
            severity_de_escalation=severity_data.get("severity_de_escalation", False),
            severity_trend_description=severity_data.get("severity_trend_description", "")
        )
