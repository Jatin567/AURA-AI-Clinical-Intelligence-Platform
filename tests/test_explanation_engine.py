from datetime import datetime, timezone

from app.explanation import ExplanationEngine, ExplanationFormatter
from app.models.triage import TriageLevel
from app.reasoning.models import (
    ClinicalReasoningOutput,
    ConditionMatch,
    MissingInformation,
    RiskFactor,
)


def build_reasoning_output() -> ClinicalReasoningOutput:
    return ClinicalReasoningOutput(
        possible_conditions=[
            ConditionMatch(
                name="Pneumonia",
                confidence=0.62,
                icd10_code="J18.9",
                category="Respiratory",
                supporting_symptoms=["fever", "cough"],
                conflicting_symptoms=["runny nose"],
                base_score=0.6,
                risk_score_modifier=0.05,
                references=["Example respiratory guideline"],
            ),
            ConditionMatch(
                name="Influenza",
                confidence=0.45,
                icd10_code="J11.1",
                category="Infectious Disease",
                supporting_symptoms=["fever"],
                conflicting_symptoms=[],
                base_score=0.45,
                risk_score_modifier=0.0,
                references=["Example influenza guideline"],
            ),
        ],
        risk_factors=[
            RiskFactor(
                factor_name="Elderly Age",
                description="advanced age may increase risk of complications.",
                risk_weight=0.2,
                affected_condition="Respiratory",
            )
        ],
        missing_information=[
            MissingInformation(
                field_name="symptom_duration",
                clinical_relevance="Duration helps distinguish acute from persistent illness.",
                impact_on_reasoning="Confidence is lower without onset timing.",
            )
        ],
        evaluated_at=datetime.now(timezone.utc),
    )


def test_explanation_engine_generates_complete_structured_explanation():
    engine = ExplanationEngine()

    explanation = engine.generate(build_reasoning_output(), TriageLevel.URGENT)

    assert explanation.source == "deterministic_clinical_reasoning"
    assert explanation.executive_summary.leading_condition == "Pneumonia"
    assert "Pneumonia is currently the leading possible condition" in explanation.executive_summary.summary
    assert "not a confirmed diagnosis" in explanation.executive_summary.diagnosis_notice
    assert len(explanation.possible_conditions) == 2
    assert len(explanation.risk_factors) == 1
    assert len(explanation.missing_information) == 1
    assert len(explanation.recommendations) == 1
    assert explanation.disclaimer.informational_only
    assert explanation.disclaimer.not_a_diagnosis
    assert explanation.disclaimer.seek_professional_care


def test_condition_explanations_include_supporting_and_conflicting_findings():
    explanation = ExplanationEngine().generate(build_reasoning_output(), TriageLevel.ROUTINE)

    pneumonia = explanation.possible_conditions[0]
    influenza = explanation.possible_conditions[1]

    assert pneumonia.condition_name == "Pneumonia"
    assert pneumonia.confidence_percent == 62
    assert pneumonia.supporting_findings == ["fever", "cough"]
    assert pneumonia.conflicting_findings == ["runny nose"]
    assert "Conflicting findings include runny nose" in pneumonia.explanation

    assert influenza.confidence_percent == 45
    assert "No conflicting findings were identified" in influenza.explanation


def test_risk_factors_and_missing_information_are_human_readable():
    explanation = ExplanationEngine().generate(build_reasoning_output(), TriageLevel.ROUTINE)

    assert "Elderly Age may affect clinical risk" in explanation.risk_factors[0].explanation
    assert "Risk weight: 0.2" in explanation.risk_factors[0].explanation
    assert explanation.missing_information[0].startswith("symptom_duration:")
    assert "Confidence is lower without onset timing" in explanation.missing_information[0]


def test_emergency_recommendation_and_safety_notice_are_deterministic():
    explanation = ExplanationEngine().generate(build_reasoning_output(), TriageLevel.EMERGENCY)

    recommendation = explanation.recommendations[0]
    safety_notice = explanation.safety_notices[0]

    assert recommendation.severity == "EMERGENCY"
    assert recommendation.title == "Seek Emergency Care Immediately"
    assert recommendation.timeframe == "Now"
    assert safety_notice.immediate_action_required is True
    assert "Seek emergency care immediately" in safety_notice.message


def test_urgent_recommendation_has_prompt_care_notice():
    explanation = ExplanationEngine().generate(build_reasoning_output(), TriageLevel.URGENT)

    recommendation = explanation.recommendations[0]

    assert recommendation.severity == "URGENT"
    assert recommendation.timeframe == "Within 24 hours"
    assert len(explanation.safety_notices) == 1
    assert explanation.safety_notices[0].severity == "URGENT"


def test_routine_recommendation_has_no_emergency_notice():
    explanation = ExplanationEngine().generate(build_reasoning_output(), TriageLevel.ROUTINE)

    recommendation = explanation.recommendations[0]

    assert recommendation.severity == "ROUTINE"
    assert recommendation.title == "Schedule a Clinical Appointment"
    assert explanation.safety_notices == []


def test_home_care_maps_to_self_care_recommendation_without_api_enum_change():
    explanation = ExplanationEngine().generate(build_reasoning_output(), TriageLevel.HOME_CARE)

    recommendation = explanation.recommendations[0]

    assert recommendation.severity == "SELF_CARE"
    assert recommendation.title == "Self Care With Monitoring"
    assert explanation.safety_notices == []


def test_string_self_care_alias_is_supported_for_future_internal_callers():
    explanation = ExplanationEngine().generate(build_reasoning_output(), "SELF_CARE")

    assert explanation.recommendations[0].severity == "SELF_CARE"


def test_no_conditions_summary_is_safe_and_non_diagnostic():
    empty_output = ClinicalReasoningOutput(
        possible_conditions=[],
        risk_factors=[],
        missing_information=[],
    )

    explanation = ExplanationEngine().generate(empty_output, TriageLevel.HOME_CARE)

    assert explanation.executive_summary.leading_condition is None
    assert explanation.executive_summary.confidence is None
    assert "does not identify a clear leading possible condition" in explanation.executive_summary.summary
    assert explanation.possible_conditions == []


def test_formatter_renders_markdown_plain_text_and_json():
    explanation = ExplanationEngine().generate(build_reasoning_output(), TriageLevel.URGENT)
    formatter = ExplanationFormatter()

    markdown = formatter.to_markdown(explanation)
    plain_text = formatter.to_plain_text(explanation)
    structured = formatter.to_json(explanation)
    json_string = formatter.to_json_string(explanation)

    assert "# Clinical Explanation" in markdown
    assert "## Recommendations" in markdown
    assert "Clinical Explanation" in plain_text
    assert "Seek Prompt Medical Care" in plain_text
    assert structured["executive_summary"]["leading_condition"] == "Pneumonia"
    assert structured["recommendations"][0]["severity"] == "URGENT"
    assert '"leading_condition": "Pneumonia"' in json_string

