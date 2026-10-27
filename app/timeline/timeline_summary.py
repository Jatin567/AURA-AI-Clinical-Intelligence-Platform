from app.timeline.models import TrendAnalysisResult, TimelineSummary

class TimelineSummaryGenerator:
    """
    Deterministically generates text-based summaries from TrendAnalysisResults.
    """

    @classmethod
    def generate(cls, trends: TrendAnalysisResult) -> TimelineSummary:
        # Severity Summary
        severity_summary = trends.severity_trend_description

        # Symptom Summary
        symptom_parts = []
        if trends.recurring_symptoms:
            symptom_parts.append(f"Recurring symptoms: {', '.join(trends.recurring_symptoms)}.")
        if trends.newly_introduced_symptoms:
            symptom_parts.append(f"New symptoms reported: {', '.join(trends.newly_introduced_symptoms)}.")
        if trends.resolved_symptoms:
            symptom_parts.append(f"Resolved symptoms: {', '.join(trends.resolved_symptoms)}.")
        symptom_summary = " ".join(symptom_parts) if symptom_parts else "No significant symptom trends detected."

        # Condition Summary
        condition_parts = []
        if trends.recurring_conditions:
            condition_parts.append(f"Recurring conditions evaluated: {', '.join(trends.recurring_conditions)}.")
        for cond, diff in trends.confidence_increases.items():
            condition_parts.append(f"Confidence for '{cond}' has increased by {diff:.2f}.")
        for cond, diff in trends.confidence_decreases.items():
            condition_parts.append(f"Confidence for '{cond}' has decreased by {diff:.2f}.")
        condition_summary = " ".join(condition_parts) if condition_parts else "Condition confidence stable."

        # Recommendation Summary (Placeholders for now, normally mapped from last assessment's recommendations)
        recommendation_summary = "Adhere to the most recent clinical recommendations."

        overall = f"{trends.assessment_frequency} {severity_summary}"

        return TimelineSummary(
            overall_summary=overall,
            severity_summary=severity_summary,
            symptom_summary=symptom_summary,
            condition_summary=condition_summary,
            recommendation_summary=recommendation_summary
        )
