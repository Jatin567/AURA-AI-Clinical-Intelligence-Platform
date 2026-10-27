from typing import Any
from app.workspace.models import WorkspaceClinicalExplanation
from app.explanation.models import ClinicalExplanation

class SummaryBuilder:
    """Adapts ClinicalExplanation into WorkspaceClinicalExplanation."""
    
    @staticmethod
    def adapt(explanation: ClinicalExplanation) -> WorkspaceClinicalExplanation:
        exec_summary = ""
        if explanation.executive_summary:
            exec_summary = explanation.executive_summary.summary

        findings = []
        if explanation.possible_conditions:
            for condition in explanation.possible_conditions:
                findings.extend(condition.supporting_findings)

        risk_factors = []
        if explanation.risk_factors:
            risk_factors = [r.factor_name for r in explanation.risk_factors]
            
        missing_info = explanation.missing_information if explanation.missing_information else []

        return WorkspaceClinicalExplanation(
            executive_summary=exec_summary,
            supporting_findings=list(set(findings)), # Deduplicate
            risk_factors=risk_factors,
            missing_information=missing_info
        )
