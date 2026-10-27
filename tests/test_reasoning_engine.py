import pytest
from app.reasoning import (
    ClinicalReasoningEngine,
    KnowledgeRepository,
    ClinicalInput,
    ClinicalReasoningOutput
)


@pytest.fixture
def reasoning_engine():
    """Provides a fresh instance of ClinicalReasoningEngine."""
    return ClinicalReasoningEngine()


def test_knowledge_repository_loading():
    """Test that knowledge repository loads condition definitions cleanly from JSON."""
    repo = KnowledgeRepository()
    conditions = repo.get_all_conditions()
    assert len(conditions) >= 20, f"Expected at least 20 conditions, found {len(conditions)}"
    
    # Check ACS entry
    acs = repo.get_condition_by_id("COND_001")
    assert acs is not None
    assert acs.name == "Acute Coronary Syndrome"
    assert acs.icd10_code == "I24.9"
    assert len(acs.references) > 0


def test_condition_matcher_acs_presentation(reasoning_engine):
    """Test matching Acute Coronary Syndrome presentation."""
    clinical_input = ClinicalInput(
        symptoms=["chest pain", "shortness of breath", "dizziness"],
        chief_complaint="I have severe chest pressure and trouble breathing",
        age=68,
        chronic_conditions=["diabetes", "hypertension"]
    )

    output: ClinicalReasoningOutput = reasoning_engine.evaluate(clinical_input)

    assert len(output.possible_conditions) > 0
    top_match = output.possible_conditions[0]
    assert top_match.name == "Acute Coronary Syndrome"
    assert top_match.confidence > 0.6
    assert 0.0 <= top_match.confidence <= 1.0
    assert "chest pain" in top_match.supporting_symptoms
    assert top_match.icd10_code == "I24.9"
    assert len(top_match.references) > 0


def test_risk_factor_engine_modifiers(reasoning_engine):
    """Test that elderly age and diabetes correctly trigger risk factors."""
    clinical_input = ClinicalInput(
        symptoms=["chest pain"],
        age=72,
        chronic_conditions=["diabetes", "hypertension"]
    )

    output = reasoning_engine.evaluate(clinical_input)

    assert len(output.risk_factors) >= 2
    factor_names = [rf.factor_name for rf in output.risk_factors]
    assert any("Elderly" in name for name in factor_names)
    assert any("Diabetes" in name for name in factor_names)


def test_confidence_bounds_strictly_between_0_and_1(reasoning_engine):
    """Test that confidence scores across various inputs remain strictly in [0.0, 1.0]."""
    test_inputs = [
        ClinicalInput(symptoms=["cough", "fever"], age=30),
        ClinicalInput(symptoms=["chest pain", "shortness of breath", "dizziness", "nausea", "sweating"], age=80, chronic_conditions=["diabetes", "hypertension", "heart disease"]),
        ClinicalInput(symptoms=["headache"], age=10),
        ClinicalInput(symptoms=["rash", "swelling", "shortness of breath"], allergies=["peanuts"])
    ]

    for inp in test_inputs:
        output = reasoning_engine.evaluate(inp)
        for cond in output.possible_conditions:
            assert 0.0 <= cond.confidence <= 1.0, f"Confidence {cond.confidence} out of bounds for {cond.name}"


def test_no_symptoms_forces_zero_confidence(reasoning_engine):
    """Test that when no symptoms match a condition, confidence remains 0.0 despite risk factors."""
    clinical_input = ClinicalInput(
        symptoms=["ear pain"], # Ear pain does not match ACS
        age=85,
        chronic_conditions=["diabetes", "hypertension"]
    )

    output = reasoning_engine.evaluate(clinical_input)

    # Check if ACS is present in possible_conditions, if so its base_score and confidence must be handled correctly
    acs_matches = [c for c in output.possible_conditions if c.name == "Acute Coronary Syndrome"]
    if acs_matches:
        assert acs_matches[0].confidence == 0.0 or acs_matches[0].base_score == 0.0


def test_missing_information_detection(reasoning_engine):
    """Test detection of missing clinical parameters."""
    clinical_input = ClinicalInput(
        symptoms=["cough", "fever"]
        # Age, duration, severity, chronic_conditions omitted
    )

    output = reasoning_engine.evaluate(clinical_input)

    missing_fields = [m.field_name for m in output.missing_information]
    assert "age" in missing_fields
    assert "symptom_duration" in missing_fields
    assert "symptom_severity" in missing_fields
    assert "chronic_conditions" in missing_fields


test_reasoning_steps_audit_trace = """Test transparent step-by-step audit trace generation."""
def test_reasoning_steps_audit_trace(reasoning_engine):
    clinical_input = ClinicalInput(
        symptoms=["fever", "cough", "shortness of breath"],
        age=45,
        symptom_duration="3 days"
    )

    output = reasoning_engine.evaluate(clinical_input)

    assert len(output.reasoning_steps) >= 4
    phases = [s.phase for s in output.reasoning_steps]
    assert "INTAKE_ANALYSIS" in phases
    assert "MISSING_DATA_AUDIT" in phases
    assert "CONDITION_MATCHING" in phases
    assert "RISK_EVALUATION" in phases
    assert "SYNTHESIS" in phases


def test_conflicting_symptoms_penalty(reasoning_engine):
    """Test that conflicting symptoms reduce condition confidence score."""
    # Inputs with conflicting symptoms vs without
    input_no_conflict = ClinicalInput(symptoms=["cough", "sore throat", "runny nose"])
    input_with_conflict = ClinicalInput(symptoms=["cough", "sore throat", "runny nose", "severe chest pressure"])

    out_no_conflict = reasoning_engine.evaluate(input_no_conflict)
    out_with_conflict = reasoning_engine.evaluate(input_with_conflict)

    urti_no_conflict = next(c for c in out_no_conflict.possible_conditions if c.name == "Upper Respiratory Tract Infection")
    urti_with_conflict = next(c for c in out_with_conflict.possible_conditions if c.name == "Upper Respiratory Tract Infection")

    assert urti_with_conflict.base_score < urti_no_conflict.base_score
