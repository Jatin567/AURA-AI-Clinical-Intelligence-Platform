import json

from app.explanation.models import ClinicalExplanation


class ExplanationFormatter:
    """Renders ClinicalExplanation in report-friendly formats."""

    def to_json(self, explanation: ClinicalExplanation) -> dict:
        return explanation.to_structured_json()

    def to_json_string(self, explanation: ClinicalExplanation, indent: int = 2) -> str:
        return json.dumps(self.to_json(explanation), indent=indent)

    def to_markdown(self, explanation: ClinicalExplanation) -> str:
        lines = [
            "# Clinical Explanation",
            "",
            "## Executive Summary",
            explanation.executive_summary.summary,
            "",
            "## Possible Conditions",
        ]

        if explanation.possible_conditions:
            for condition in explanation.possible_conditions:
                lines.extend([
                    f"### {condition.condition_name}",
                    f"- Confidence: {condition.confidence_percent}%",
                    f"- Supporting findings: {self._list_or_none(condition.supporting_findings)}",
                    f"- Conflicting findings: {self._list_or_none(condition.conflicting_findings)}",
                    f"- Explanation: {condition.explanation}",
                ])
        else:
            lines.append("No possible conditions were identified from the available information.")

        lines.extend(["", "## Risk Factors"])
        if explanation.risk_factors:
            for risk in explanation.risk_factors:
                lines.append(f"- {risk.explanation}")
        else:
            lines.append("No additional risk factors were identified.")

        lines.extend(["", "## Missing Information"])
        if explanation.missing_information:
            for item in explanation.missing_information:
                lines.append(f"- {item}")
        else:
            lines.append("No major missing information was identified.")

        lines.extend(["", "## Recommendations"])
        for recommendation in explanation.recommendations:
            lines.extend([
                f"### {recommendation.title}",
                f"- Severity: {recommendation.severity}",
                f"- Action: {recommendation.action}",
                f"- Timeframe: {recommendation.timeframe}",
                f"- Rationale: {recommendation.rationale}",
            ])

        lines.extend(["", "## Safety Notices"])
        if explanation.safety_notices:
            for notice in explanation.safety_notices:
                lines.append(f"- {notice.title}: {notice.message}")
        else:
            lines.append("No emergency safety notice was generated.")

        lines.extend([
            "",
            "## Disclaimer",
            f"- {explanation.disclaimer.informational_only}",
            f"- {explanation.disclaimer.not_a_diagnosis}",
            f"- {explanation.disclaimer.seek_professional_care}",
        ])

        return "\n".join(lines)

    def to_plain_text(self, explanation: ClinicalExplanation) -> str:
        lines = [
            "Clinical Explanation",
            "",
            "Executive Summary",
            explanation.executive_summary.summary,
            "",
            "Possible Conditions",
        ]

        if explanation.possible_conditions:
            for condition in explanation.possible_conditions:
                lines.extend([
                    f"{condition.condition_name}",
                    f"Confidence: {condition.confidence_percent}%",
                    f"Supporting findings: {self._list_or_none(condition.supporting_findings)}",
                    f"Conflicting findings: {self._list_or_none(condition.conflicting_findings)}",
                    condition.explanation,
                ])
        else:
            lines.append("No possible conditions were identified from the available information.")

        lines.extend(["", "Risk Factors"])
        lines.extend(
            [risk.explanation for risk in explanation.risk_factors]
            or ["No additional risk factors were identified."]
        )

        lines.extend(["", "Missing Information"])
        lines.extend(
            explanation.missing_information
            or ["No major missing information was identified."]
        )

        lines.extend(["", "Recommendations"])
        for recommendation in explanation.recommendations:
            lines.extend([
                recommendation.title,
                f"Severity: {recommendation.severity}",
                f"Action: {recommendation.action}",
                f"Timeframe: {recommendation.timeframe}",
                f"Rationale: {recommendation.rationale}",
            ])

        lines.extend(["", "Safety Notices"])
        lines.extend(
            [f"{notice.title}: {notice.message}" for notice in explanation.safety_notices]
            or ["No emergency safety notice was generated."]
        )

        lines.extend([
            "",
            "Disclaimer",
            explanation.disclaimer.informational_only,
            explanation.disclaimer.not_a_diagnosis,
            explanation.disclaimer.seek_professional_care,
        ])

        return "\n".join(lines)

    def _list_or_none(self, values: list[str]) -> str:
        return ", ".join(values) if values else "None"

