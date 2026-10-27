from app.explanation.explanation_templates import DISCLAIMER, SAFETY_NOTICE_TEMPLATES
from app.explanation.models import Disclaimer, SafetyNotice
from app.models.triage import TriageLevel


class DisclaimerEngine:
    """Builds mandatory disclaimers and severity-driven safety notices."""

    def build_disclaimer(self) -> Disclaimer:
        return Disclaimer(**DISCLAIMER)

    def build_safety_notice(self, severity: TriageLevel) -> SafetyNotice | None:
        template = SAFETY_NOTICE_TEMPLATES.get(severity)
        if not template:
            return None
        return SafetyNotice(**template)

