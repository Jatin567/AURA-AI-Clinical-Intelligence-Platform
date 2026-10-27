import pytest
from datetime import date, datetime, timezone
from app.patients import PatientProfile, MedicalHistory, MedicationList, AllergyList
from app.patients.profile_service import ProfileService
from app.patients.repository import InMemoryPatientRepository
from app.timeline import TimelineEngine, InMemoryTimelineRepository, TimelineEntry, TimelineSummary, TrendAnalysisResult
from app.explanation.models import ClinicalExplanation as ReportingClinicalExplanation, ExecutiveSummary
from app.reporting.models import ClinicalReport, ReportMetadata, PatientSummary, ReasoningSummary, InterviewSummary, ClinicalDisclaimer, AuditMetadata
from app.workspace import WorkspaceService

@pytest.fixture
def profile_service():
    repo = InMemoryPatientRepository()
    svc = ProfileService(repo)
    profile = PatientProfile(
        patient_id="p1",
        user_id="u1",
        full_name="Workspace Doe",
        date_of_birth=date(1985, 5, 5),
        biological_sex="F",
        medical_history=MedicalHistory(chronic_conditions=["Asthma"]),
        allergies=AllergyList(allergies=["Peanuts"]),
        medications=MedicationList(current_medications=["Albuterol"])
    )
    svc.create_profile(profile)
    return svc

@pytest.fixture
def timeline_engine():
    repo = InMemoryTimelineRepository()
    engine = TimelineEngine(repo)
    entry = TimelineEntry(
        assessment_id="hist-1",
        patient_id="p1",
        timestamp=datetime.now(timezone.utc),
        severity="ROUTINE",
        top_condition="Common Cold",
        report_reference="fake_report_obj"
    )
    repo.add_entry(entry)
    return engine

@pytest.fixture
def mock_current_report():
    return ClinicalReport(
        metadata=ReportMetadata(
            assessment_id="curr-1",
            session_id="s1",
            generation_timestamp=datetime.now(timezone.utc),
            app_version="1",
            knowledge_base_version="1",
            reasoning_engine_version="1",
            explanation_engine_version="1"
        ),
        patient_summary=PatientSummary(chief_complaint="Coughing a lot"),
        interview_summary=InterviewSummary(turn_count=5),
        evidence_summary=[],
        clinical_reasoning_summary=ReasoningSummary(
            leading_condition="Bronchitis",
            confidence=0.85,
            summary="Matches symptoms."
        ),
        possible_conditions=[],
        risk_factors=[],
        missing_information=[],
        severity="URGENT",
        recommendations=[],
        safety_notices=[],
        clinical_disclaimer=ClinicalDisclaimer(
            informational_only="Info",
            not_a_diagnosis="Not dx",
            seek_professional_care="Seek help"
        ),
        audit_metadata=AuditMetadata(reasoning_steps=[])
    )

from app.explanation.models import ClinicalExplanation as ReportingClinicalExplanation, ExecutiveSummary, Disclaimer

@pytest.fixture
def mock_current_explanation():
    return ReportingClinicalExplanation(
        executive_summary=ExecutiveSummary(
            leading_condition="Bronchitis",
            summary="Acute bronchitis likely.",
            diagnosis_notice="Not a diagnosis"
        ),
        possible_conditions=[],
        risk_factors=[],
        missing_information=[],
        recommendations=[],
        safety_notices=[],
        disclaimer=Disclaimer(
            informational_only="Info",
            not_a_diagnosis="Not a dx",
            seek_professional_care="Seek help"
        )
    )

def test_workspace_build(profile_service, timeline_engine, mock_current_report, mock_current_explanation):
    service = WorkspaceService(profile_service, timeline_engine)
    
    workspace = service.build_workspace("p1", mock_current_report, mock_current_explanation)
    
    assert workspace.metadata.patient_id == "p1"
    assert workspace.metadata.current_assessment_id == "curr-1"
    
    # Check Patient mapping
    assert workspace.patient.full_name == "Workspace Doe"
    assert "Asthma" in workspace.patient.chronic_conditions
    assert "Peanuts" in workspace.patient.allergies
    
    # Check Assessment mapping
    assert workspace.current_assessment.severity == "URGENT"
    assert workspace.current_assessment.top_condition == "Bronchitis"
    assert workspace.current_assessment.confidence == 0.85
    
    # Check Timeline mapping
    assert len(workspace.timeline.historical_assessments) == 1
    assert workspace.timeline.historical_assessments[0].assessment_id == "hist-1"
    
    # Check Reports mapping
    assert workspace.reports.current_report_reference == mock_current_report
    assert "fake_report_obj" in workspace.reports.historical_report_references
    
    # Check Explanations mapping
    assert workspace.clinical_explanation.executive_summary == "Acute bronchitis likely."
    
    # Check Actions
    assert workspace.actions.can_export_pdf is False
    assert workspace.actions.can_compare_assessments is False

def test_workspace_missing_timeline(profile_service, mock_current_report, mock_current_explanation):
    # Empty timeline engine
    empty_engine = TimelineEngine(InMemoryTimelineRepository())
    service = WorkspaceService(profile_service, empty_engine)
    
    # Should not raise exception
    workspace = service.build_workspace("p1", mock_current_report, mock_current_explanation)
    
    assert len(workspace.timeline.historical_assessments) == 0
    assert len(workspace.reports.historical_report_references) == 0
    # Trends should be empty but safely instantiated
    assert workspace.trends.symptom_trends == ""
    assert workspace.trends.severity_trends == ""
