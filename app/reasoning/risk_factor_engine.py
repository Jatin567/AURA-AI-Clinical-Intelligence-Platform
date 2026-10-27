from typing import List, Dict, Optional, Tuple
from app.reasoning.models import ClinicalInput, RiskFactor, ConditionDefinition


class RiskFactorEngine:
    """
    Evaluates patient demographics, chronic conditions, and physiological states
    to compute deterministic risk weights and modifiers.
    Does NOT use machine learning or LLM models.
    """

    def evaluate_risk_factors(
        self, clinical_input: ClinicalInput, conditions: List[ConditionDefinition]
    ) -> Tuple[List[RiskFactor], Dict[str, float]]:
        """
        Evaluates risk factors present in clinical input against matched conditions.
        
        Returns:
            Tuple containing:
            - List of identified RiskFactor records for explainability
            - Dictionary mapping condition_id -> cumulative risk modifier float
        """
        risk_factors: List[RiskFactor] = []
        condition_modifiers: Dict[str, float] = {cond.id: 0.0 for cond in conditions}

        # Normalize patient chronic condition strings
        patient_conditions = [c.lower().strip() for c in clinical_input.chronic_conditions]
        patient_meds = [m.lower().strip() for m in clinical_input.medications]
        patient_allergies = [a.lower().strip() for a in clinical_input.allergies]

        # 1. Demographic: Age-based risk factor evaluation
        age = clinical_input.age
        if age is not None:
            if age >= 65:
                rf = RiskFactor(
                    factor_name="Elderly Age (>= 65)",
                    description="Advanced age increases vulnerability to cardiovascular events, severe infections, and metabolic complications.",
                    risk_weight=0.2,
                    affected_condition="Multiple"
                )
                risk_factors.append(rf)
                self._apply_modifier_by_key(conditions, condition_modifiers, "age_over_65", 0.2)

            elif age < 1:
                rf = RiskFactor(
                    factor_name="Infant Age (< 1 year)",
                    description="Infants have immature immune and thermoregulatory systems, elevating risk for rapid dehydration and sepsis.",
                    risk_weight=0.25,
                    affected_condition="Multiple"
                )
                risk_factors.append(rf)
                self._apply_modifier_by_key(conditions, condition_modifiers, "infant", 0.25)

        # 2. Chronic Condition: Diabetes
        if any("diabet" in c for c in patient_conditions):
            rf = RiskFactor(
                factor_name="Diabetes Mellitus",
                description="Pre-existing diabetes impairs microvascular perfusion and immune function, worsening cardiovascular and infection outcomes.",
                risk_weight=0.25,
                affected_condition="Cardiovascular & Metabolic"
            )
            risk_factors.append(rf)
            self._apply_modifier_by_key(conditions, condition_modifiers, "diabetes", 0.25)

        # 3. Chronic Condition: Hypertension
        if any("hyperten" in c or "high blood pressure" in c for c in patient_conditions):
            rf = RiskFactor(
                factor_name="Hypertension",
                description="Chronic elevated blood pressure accelerates vascular disease, stroke, and cardiac wall stress.",
                risk_weight=0.25,
                affected_condition="Hypertensive Crisis & ACS"
            )
            risk_factors.append(rf)
            self._apply_modifier_by_key(conditions, condition_modifiers, "hypertension", 0.25)

        # 4. Chronic Condition: Heart Disease / CAD
        if any("heart" in c or "cad" in c or "cardiac" in c for c in patient_conditions):
            rf = RiskFactor(
                factor_name="Coronary / Organic Heart Disease",
                description="Prior cardiac pathology significantly lowers ischemic threshold during acute distress.",
                risk_weight=0.3,
                affected_condition="Acute Coronary Syndrome & PE"
            )
            risk_factors.append(rf)
            self._apply_modifier_by_key(conditions, condition_modifiers, "heart disease", 0.3)

        # 5. Chronic Condition: Asthma / COPD
        if any("asthma" in c or "copd" in c for c in patient_conditions):
            rf = RiskFactor(
                factor_name="Chronic Airway Disease (Asthma/COPD)",
                description="Airway hyperreactivity exacerbates acute respiratory distress and pulmonary infections.",
                risk_weight=0.25,
                affected_condition="Asthma Exacerbation & Pneumonia"
            )
            risk_factors.append(rf)
            self._apply_modifier_by_key(conditions, condition_modifiers, "asthma", 0.25)
            self._apply_modifier_by_key(conditions, condition_modifiers, "copd", 0.25)

        # 6. Immunocompromised State
        if any("immun" in c or "chemo" in c or "steroid" in m for c in patient_conditions for m in patient_meds):
            rf = RiskFactor(
                factor_name="Immunocompromised Status",
                description="Suppressed immune function increases risk for fulminant pulmonary and systemic infections.",
                risk_weight=0.3,
                affected_condition="Pneumonia & Gastroenteritis"
            )
            risk_factors.append(rf)
            self._apply_modifier_by_key(conditions, condition_modifiers, "immunocompromised", 0.3)

        # 7. Known Allergies
        if patient_allergies and not any(a == "none" for a in patient_allergies):
            rf = RiskFactor(
                factor_name="Documented Atopy / Allergies",
                description="Known allergic sensitivity increases risk for severe systemic anaphylaxis or hypersensitivity.",
                risk_weight=0.2,
                affected_condition="Anaphylaxis & Allergic Rhinitis"
            )
            risk_factors.append(rf)
            self._apply_modifier_by_key(conditions, condition_modifiers, "allergies", 0.2)

        return risk_factors, condition_modifiers

    def _apply_modifier_by_key(
        self,
        conditions: List[ConditionDefinition],
        condition_modifiers: Dict[str, float],
        risk_key: str,
        default_weight: float
    ) -> None:
        """Applies risk modifier to conditions that declare matching risk keys in the repository."""
        for cond in conditions:
            if risk_key in cond.risk_modifiers:
                # Use condition-specific weight from repository if present, otherwise default_weight
                assigned_weight = cond.risk_modifiers[risk_key]
                condition_modifiers[cond.id] += assigned_weight
