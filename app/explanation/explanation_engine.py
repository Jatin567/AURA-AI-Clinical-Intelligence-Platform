from typing import List, Optional, Union

from app.explanation.disclaimer_engine import DisclaimerEngine
from app.explanation.explanation_templates import (
    CONDITION_WITH_EVIDENCE,
    CONDITION_WITHOUT_CONFLICTS,
    CONDITION_WITHOUT_SUPPORT,
    DIAGNOSIS_NOTICE,
    LEADING_CONDITION_SUMMARY,
    MISSING_INFORMATION,
    NO_CONDITION_SUMMARY,
    RISK_EXPLANATION,
)
from app.explanation.models import (
    ClinicalExplanation,
    ConditionExplanation,
    ExecutiveSummary,
    RiskExplanation,
)
from app.explanation.recommendation_engine import RecommendationEngine
from app.models.triage import TriageLevel
from app.reasoning.models import ClinicalReasoningOutput, ConditionMatch


class ExplanationEngine:
    """
    Deterministically transforms ClinicalReasoningOutput into a patient-readable
    structured explanation.

    This engine does not call any LLM provider and does not make medical
    decisions. Severity must come from the authoritative classifier.
    """

    def __init__(
        self,
        recommendation_engine: Optional[RecommendationEngine] = None,
        disclaimer_engine: Optional[DisclaimerEngine] = None,
    ):
        self.recommendation_engine = recommendation_engine or RecommendationEngine()
        self.disclaimer_engine = disclaimer_engine or DisclaimerEngine()

    def generate(
        self,
        reasoning_output: ClinicalReasoningOutput,
        severity: Union[TriageLevel, str],
    ) -> ClinicalExplanation:
        level = self.recommendation_engine._normalize_severity(severity)
        possible_conditions = [
            self._explain_condition(condition)
            for condition in reasoning_output.possible_conditions
        ]
        risk_factors = [
            RiskExplanation(
                factor_name=risk.factor_name,
                description=risk.description,
                risk_weight=risk.risk_weight,
                affected_condition=risk.affected_condition,
                explanation=RISK_EXPLANATION.format(
                    factor_name=risk.factor_name,
                    description=risk.description,
                    risk_weight=risk.risk_weight,
                ),
            )
            for risk in reasoning_output.risk_factors
        ]

        safety_notice = self.disclaimer_engine.build_safety_notice(level)
        safety_notices = [safety_notice] if safety_notice else []

        return ClinicalExplanation(
            executive_summary=self._build_executive_summary(reasoning_output),
            possible_conditions=possible_conditions,
            risk_factors=risk_factors,
            missing_information=self._build_missing_information(reasoning_output),
            recommendations=[self.recommendation_engine.generate(level)],
            safety_notices=safety_notices,
            disclaimer=self.disclaimer_engine.build_disclaimer(),
        )

    def _build_executive_summary(
        self,
        reasoning_output: ClinicalReasoningOutput,
    ) -> ExecutiveSummary:
        leading = self._leading_condition(reasoning_output.possible_conditions)
        if leading is None:
            return ExecutiveSummary(
                leading_condition=None,
                confidence=None,
                summary=NO_CONDITION_SUMMARY,
                diagnosis_notice=DIAGNOSIS_NOTICE,
            )

        return ExecutiveSummary(
            leading_condition=leading.name,
            confidence=leading.confidence,
            summary=LEADING_CONDITION_SUMMARY.format(condition_name=leading.name),
            diagnosis_notice=DIAGNOSIS_NOTICE,
        )

    def _leading_condition(
        self,
        conditions: List[ConditionMatch],
    ) -> Optional[ConditionMatch]:
        if not conditions:
            return None
        return max(conditions, key=lambda condition: condition.confidence)

    def _explain_condition(self, condition: ConditionMatch) -> ConditionExplanation:
        confidence_percent = round(condition.confidence * 100)
        supporting = self._join_findings(condition.supporting_symptoms)
        conflicting = self._join_findings(condition.conflicting_symptoms)

        if condition.supporting_symptoms and condition.conflicting_symptoms:
            explanation = CONDITION_WITH_EVIDENCE.format(
                condition_name=condition.name,
                confidence_percent=confidence_percent,
                supporting=supporting,
                conflicting=conflicting,
            )
        elif condition.supporting_symptoms:
            explanation = CONDITION_WITHOUT_CONFLICTS.format(
                condition_name=condition.name,
                confidence_percent=confidence_percent,
                supporting=supporting,
            )
        else:
            explanation = CONDITION_WITHOUT_SUPPORT.format(
                condition_name=condition.name,
                confidence_percent=confidence_percent,
            )

        return ConditionExplanation(
            condition_name=condition.name,
            confidence=condition.confidence,
            confidence_percent=confidence_percent,
            supporting_findings=condition.supporting_symptoms,
            conflicting_findings=condition.conflicting_symptoms,
            explanation=explanation,
        )

    def _build_missing_information(
        self,
        reasoning_output: ClinicalReasoningOutput,
    ) -> List[str]:
        return [
            MISSING_INFORMATION.format(
                field_name=item.field_name,
                clinical_relevance=item.clinical_relevance,
                impact_on_reasoning=item.impact_on_reasoning,
            )
            for item in reasoning_output.missing_information
        ]

    def _join_findings(self, findings: List[str]) -> str:
        if not findings:
            return "none"
        if len(findings) == 1:
            return findings[0]
        return ", ".join(findings[:-1]) + f", and {findings[-1]}"

