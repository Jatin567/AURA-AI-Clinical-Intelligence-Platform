import logging
from datetime import datetime, timezone
from typing import List, Optional
from app.reasoning.models import (
    ClinicalInput,
    ClinicalReasoningOutput,
    ConditionMatch,
    RiskFactor,
    MissingInformation,
    ReasoningStep
)
from app.reasoning.knowledge_repository import KnowledgeRepository
from app.reasoning.condition_matcher import ConditionMatcher
from app.reasoning.risk_factor_engine import RiskFactorEngine
from app.reasoning.confidence_engine import ConfidenceEngine

logger = logging.getLogger("aura.reasoning.engine")


class ClinicalReasoningEngine:
    """
    Main orchestrator for the internal Clinical Reasoning Engine.
    Executes deterministic, multi-stage clinical reasoning prior to LLM explanation.
    
    Guarantees:
    - 100% deterministic (no LLM, no machine learning).
    - Data-driven knowledge consuming KnowledgeRepository.
    - Every decision is transparently logged in reasoning_steps.
    - Confidence scores strictly bounded in [0.0, 1.0].
    """

    def __init__(self, repository: Optional[KnowledgeRepository] = None):
        self.repository = repository or KnowledgeRepository()
        self.condition_matcher = ConditionMatcher(self.repository)
        self.risk_engine = RiskFactorEngine()
        self.confidence_engine = ConfidenceEngine()

    def evaluate(self, clinical_input: ClinicalInput) -> ClinicalReasoningOutput:
        """
        Executes complete clinical reasoning pipeline on input presentation.
        Returns structured ClinicalReasoningOutput.
        """
        steps: List[ReasoningStep] = []
        step_counter = 1

        # Phase 1: Intake Audit & Input Normalization
        symptom_count = len(clinical_input.symptoms)
        has_cc = bool(clinical_input.chief_complaint)
        steps.append(
            ReasoningStep(
                step_number=step_counter,
                phase="INTAKE_ANALYSIS",
                description=f"Received patient clinical presentation with {symptom_count} symptom tags and chief complaint.",
                evidence=[
                    f"symptoms: {clinical_input.symptoms}",
                    f"chief_complaint: {clinical_input.chief_complaint or 'None'}",
                    f"age: {clinical_input.age if clinical_input.age is not None else 'Unspecified'}"
                ]
            )
        )
        step_counter += 1

        # Phase 2: Missing Information Audit
        missing_info = self._detect_missing_information(clinical_input)
        steps.append(
            ReasoningStep(
                step_number=step_counter,
                phase="MISSING_DATA_AUDIT",
                description=f"Evaluated input completeness. Identified {len(missing_info)} missing clinical parameters.",
                evidence=[m.field_name for m in missing_info]
            )
        )
        step_counter += 1

        # Phase 3: Condition Matching (Consuming Knowledge Repository)
        candidates = self.condition_matcher.match_conditions(clinical_input)
        matched_condition_defs = [c.condition for c in candidates]
        steps.append(
            ReasoningStep(
                step_number=step_counter,
                phase="CONDITION_MATCHING",
                description=f"Evaluated symptom tags against {len(self.repository.get_all_conditions())} repository conditions. Matched {len(candidates)} candidate conditions.",
                evidence=[f"{c.condition.name} (base_score={c.base_score})" for c in candidates]
            )
        )
        step_counter += 1

        # Phase 4: Risk Factor Evaluation
        risk_factors, risk_modifiers = self.risk_engine.evaluate_risk_factors(
            clinical_input, matched_condition_defs
        )
        steps.append(
            ReasoningStep(
                step_number=step_counter,
                phase="RISK_EVALUATION",
                description=f"Evaluated patient demographics and chronic conditions. Identified {len(risk_factors)} risk factors.",
                evidence=[f"{rf.factor_name} (+{rf.risk_weight})" for rf in risk_factors]
            )
        )
        step_counter += 1

        # Phase 5: Confidence Calculation & Normalization
        possible_conditions: List[ConditionMatch] = []
        for candidate in candidates:
            cond_id = candidate.condition.id
            modifier = risk_modifiers.get(cond_id, 0.0)
            
            conf_score = self.confidence_engine.calculate_confidence(
                base_score=candidate.base_score,
                risk_modifier=modifier
            )

            possible_conditions.append(
                ConditionMatch(
                    name=candidate.condition.name,
                    confidence=conf_score,
                    icd10_code=candidate.condition.icd10_code,
                    category=candidate.condition.category,
                    supporting_symptoms=candidate.supporting_symptoms,
                    conflicting_symptoms=candidate.conflicting_symptoms,
                    base_score=candidate.base_score,
                    risk_score_modifier=round(modifier, 4),
                    references=candidate.condition.references
                )
            )

        # Sort final possible conditions descending by confidence
        possible_conditions.sort(key=lambda x: x.confidence, reverse=True)

        steps.append(
            ReasoningStep(
                step_number=step_counter,
                phase="SYNTHESIS",
                description="Derived normalized confidence scores bounded in [0.0, 1.0] for all matched conditions.",
                evidence=[f"{match.name}: confidence={match.confidence}" for match in possible_conditions[:5]]
            )
        )

        return ClinicalReasoningOutput(
            possible_conditions=possible_conditions,
            risk_factors=risk_factors,
            missing_information=missing_info,
            reasoning_steps=steps,
            evaluated_at=datetime.now(timezone.utc)
        )

    def _detect_missing_information(self, clinical_input: ClinicalInput) -> List[MissingInformation]:
        """Identifies missing input parameters and explains their clinical significance."""
        missing: List[MissingInformation] = []

        if clinical_input.age is None:
            missing.append(
                MissingInformation(
                    field_name="age",
                    clinical_relevance="Age determines pediatric vs elderly risk stratifications (e.g. infant fever vs cardiac risk).",
                    impact_on_reasoning="Demographic age risk modifiers were omitted, defaulting to baseline risk."
                )
            )

        if not clinical_input.symptom_duration:
            missing.append(
                MissingInformation(
                    field_name="symptom_duration",
                    clinical_relevance="Duration differentiates hyperacute emergencies (e.g. stroke, anaphylaxis) from chronic presentations.",
                    impact_on_reasoning="Onset timing velocity could not be factored into acute condition weighting."
                )
            )

        if clinical_input.symptom_severity is None:
            missing.append(
                MissingInformation(
                    field_name="symptom_severity",
                    clinical_relevance="Self-reported severity scale indicates physiological distress level.",
                    impact_on_reasoning="Severity scoring threshold rules defaulted to standard symptom weightings."
                )
            )

        if not clinical_input.chronic_conditions:
            missing.append(
                MissingInformation(
                    field_name="chronic_conditions",
                    clinical_relevance="Underlying comorbidities (diabetes, hypertension) significantly adjust diagnostic probability.",
                    impact_on_reasoning="Assumed no chronic comorbid conditions present."
                )
            )

        return missing
