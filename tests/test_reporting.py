import pytest
from datetime import datetime, timezone
from app.reporting.models import AssessmentContext, ClinicalReport
from app.reporting.report_generator import ReportGenerator
from app.reporting.report_validator import ReportValidationError
from app.reporting.renderers import JSONRenderer, MarkdownRenderer, HTMLRenderer, TextRenderer
from app.reasoning.models import ClinicalReasoningOutput, ReasoningStep
from app.explanation.models import ClinicalExplanation, ExecutiveSummary, ConditionExplanation, Disclaimer, SafetyNotice

@pytest.fixture
def mock_reasoning_output():
    return ClinicalReasoningOutput(
        possible_conditions=[],
        risk_factors=[],
        missing_information=[],
        reasoning_steps=[ReasoningStep(step_number=1, phase="TEST", description="Tested logic")]
    )

@pytest.fixture
def mock_explanation():
    return ClinicalExplanation(
        executive_summary=ExecutiveSummary(
            summary="Patient presents with symptoms.",
            leading_condition="Test Condition",
            confidence=0.85,
            diagnosis_notice="Notice"
        ),
        possible_conditions=[
            ConditionExplanation(
                condition_name="Test Condition",
                confidence=0.85,
                confidence_percent=85,
                explanation="Matches symptoms.",
                supporting_findings=["finding 1"]
            )
        ],
        disclaimer=Disclaimer(
            informational_only="Info only.",
            not_a_diagnosis="Not a diagnosis.",
            seek_professional_care="Seek care."
        )
    )

@pytest.fixture
def mock_context():
    return AssessmentContext(
        assessment_id="TEST-123",
        severity="ROUTINE",
        chief_complaint="Headache",
        age=30,
        sex="Male"
    )

def test_report_generation(mock_context, mock_reasoning_output, mock_explanation):
    generator = ReportGenerator()
    report = generator.generate(mock_context, mock_reasoning_output, mock_explanation)
    
    assert report.metadata.assessment_id == "TEST-123"
    assert report.severity == "ROUTINE"
    assert report.patient_summary.chief_complaint == "Headache"
    assert len(report.possible_conditions) == 1
    assert report.possible_conditions[0].condition_name == "Test Condition"

def test_validation_failure_no_conditions(mock_context, mock_reasoning_output, mock_explanation):
    generator = ReportGenerator()
    mock_explanation.possible_conditions = []
    
    with pytest.raises(ReportValidationError) as exc:
        generator.generate(mock_context, mock_reasoning_output, mock_explanation)
    
    assert "at least one possible condition" in str(exc.value)

def test_validation_failure_emergency_no_safety_notice(mock_context, mock_reasoning_output, mock_explanation):
    generator = ReportGenerator()
    emergency_context = AssessmentContext(severity="EMERGENCY")
    
    with pytest.raises(ReportValidationError) as exc:
        generator.generate(emergency_context, mock_reasoning_output, mock_explanation)
    
    assert "EMERGENCY reports must include at least one safety notice" in str(exc.value)

def test_validation_failure_high_confidence_no_supporting_findings(mock_context, mock_reasoning_output, mock_explanation):
    generator = ReportGenerator()
    mock_explanation.possible_conditions[0].supporting_findings = []
    
    with pytest.raises(ReportValidationError) as exc:
        generator.generate(mock_context, mock_reasoning_output, mock_explanation)
    
    assert "must include supporting findings" in str(exc.value)

def test_json_renderer(mock_context, mock_reasoning_output, mock_explanation):
    report = ReportGenerator().generate(mock_context, mock_reasoning_output, mock_explanation)
    rendered = JSONRenderer().render(report)
    assert "TEST-123" in rendered
    assert "Headache" in rendered
    assert "Test Condition" in rendered

def test_markdown_renderer(mock_context, mock_reasoning_output, mock_explanation):
    report = ReportGenerator().generate(mock_context, mock_reasoning_output, mock_explanation)
    rendered = MarkdownRenderer().render(report)
    assert "# AURA Clinical Assessment Report" in rendered
    assert "**Severity:** **ROUTINE**" in rendered

def test_html_renderer(mock_context, mock_reasoning_output, mock_explanation):
    report = ReportGenerator().generate(mock_context, mock_reasoning_output, mock_explanation)
    rendered = HTMLRenderer().render(report)
    assert "<html" in rendered
    assert "<div class='meta'>Assessment ID: TEST-123</div>" in rendered
    assert "severity-routine" in rendered

def test_text_renderer(mock_context, mock_reasoning_output, mock_explanation):
    report = ReportGenerator().generate(mock_context, mock_reasoning_output, mock_explanation)
    rendered = TextRenderer().render(report)
    assert "AURA CLINICAL ASSESSMENT REPORT" in rendered
    assert "Severity:      ROUTINE" in rendered

def test_export_markdown_empty_patient():
    from app.api.export_routes import generate_markdown
    md = generate_markdown("patient_no_history_test")
    assert "# AURA Clinical Summary" in md
    assert "Unable to generate report" not in md
    assert "No prior clinical assessments recorded." in md

def test_export_markdown_with_timeline():
    from app.api.export_routes import generate_markdown
    from app.api.dependencies import timeline_engine
    from app.timeline.models import TimelineEntry
    
    entry = TimelineEntry(
        assessment_id="test_exp_1",
        patient_id="patient_with_timeline_test",
        timestamp=datetime.now(timezone.utc),
        chief_complaint="Chest pressure",
        symptoms=["Chest pressure", "Shortness of breath"],
        severity="URGENT",
        top_condition="Angina",
        recommendation="Seek immediate clinical evaluation"
    )
    timeline_engine._repository.add_entry(entry)
    
    md = generate_markdown("patient_with_timeline_test")
    assert "# AURA Clinical Summary" in md
    assert "Unable to generate report" not in md
    assert "Angina" in md or "Chest pressure" in md

def test_export_pdf_generation():
    from app.api.export_routes import generate_markdown, _build_pdf
    md = generate_markdown("patient_pdf_test")
    lines = [l.strip() for l in md.splitlines() if l.strip()]
    pdf = _build_pdf("AURA Clinical Report", lines)
    assert pdf.startswith(b"%PDF-1.4\n")
    assert pdf.endswith(b"%%EOF\n")
    assert b"Unable to generate report" not in pdf

