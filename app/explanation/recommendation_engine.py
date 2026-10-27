from typing import Union

from app.explanation.explanation_templates import RECOMMENDATION_TEMPLATES
from app.explanation.models import Recommendation
from app.models.triage import TriageLevel


class RecommendationEngine:
    """Creates deterministic recommendations from authoritative severity."""

    def generate(self, severity: Union[TriageLevel, str]) -> Recommendation:
        level = self._normalize_severity(severity)
        template = RECOMMENDATION_TEMPLATES[level]
        return Recommendation(**template)

    def _normalize_severity(self, severity: Union[TriageLevel, str]) -> TriageLevel:
        if isinstance(severity, TriageLevel):
            return severity

        normalized = severity.upper()
        if normalized in {"SELF_CARE", "NON_URGENT"}:
            return TriageLevel.HOME_CARE
        return TriageLevel(normalized)

