import pytest
from datetime import datetime, timedelta, timezone
from app.timeline import (
    SeverityLevel,
    TimelineEntry,
    InMemoryTimelineRepository,
    TimelineEngine
)

@pytest.fixture
def repo():
    return InMemoryTimelineRepository()

@pytest.fixture
def engine(repo):
    return TimelineEngine(repo)

@pytest.fixture
def sample_entries():
    now = datetime.now(timezone.utc)
    return [
        TimelineEntry(
            assessment_id="a1",
            patient_id="p1",
            timestamp=now - timedelta(days=10),
            symptoms=["fever", "cough"],
            severity="ROUTINE",
            top_condition="Viral Infection",
            top_confidence=0.7
        ),
        TimelineEntry(
            assessment_id="a2",
            patient_id="p1",
            timestamp=now - timedelta(days=5),
            symptoms=["cough", "shortness of breath"],
            severity="URGENT",
            top_condition="Viral Infection",
            top_confidence=0.8
        ),
        TimelineEntry(
            assessment_id="a3",
            patient_id="p1",
            timestamp=now,
            symptoms=["cough"],
            severity="HOME_CARE",
            top_condition="Viral Infection",
            top_confidence=0.6
        )
    ]

def test_severity_ordering():
    assert SeverityLevel.SELF_CARE == SeverityLevel.HOME_CARE
    assert SeverityLevel.ROUTINE > SeverityLevel.SELF_CARE
    assert SeverityLevel.URGENT > SeverityLevel.ROUTINE
    assert SeverityLevel.EMERGENCY > SeverityLevel.URGENT

    assert SeverityLevel.from_string("home_care") == SeverityLevel.SELF_CARE
    assert SeverityLevel.from_string("EMERGENCY") == SeverityLevel.EMERGENCY
    assert SeverityLevel.from_string("UNKNOWN") == SeverityLevel.ROUTINE

def test_timeline_sorting(repo, sample_entries):
    # Add out of order
    repo.add_entry(sample_entries[2])
    repo.add_entry(sample_entries[0])
    repo.add_entry(sample_entries[1])

    timeline = repo.get_patient_timeline("p1")
    assert len(timeline) == 3
    assert timeline[0].assessment_id == "a1"
    assert timeline[1].assessment_id == "a2"
    assert timeline[2].assessment_id == "a3"

def test_trend_analyzer_symptoms(engine, sample_entries):
    for entry in sample_entries:
        engine._repository.add_entry(entry)
    
    trends = engine.analyze_trends("p1")
    
    # a3 vs all previous (a1, a2)
    # latest: ["cough"]
    # previous: ["fever", "cough", "shortness of breath"]
    
    assert "cough" in trends.recurring_symptoms
    assert "fever" not in trends.recurring_symptoms
    assert "shortness of breath" in trends.resolved_symptoms
    
    # Actually our SymptomTrendAnalyzer resolves symptoms from immediately previous assessment.
    # a2 had "cough", "shortness of breath". a3 has "cough". So "shortness of breath" is resolved.

def test_trend_analyzer_severity(engine, sample_entries):
    # Just first two (ROUTINE -> URGENT)
    engine._repository.add_entry(sample_entries[0])
    engine._repository.add_entry(sample_entries[1])
    
    trends = engine.analyze_trends("p1")
    assert trends.severity_escalation is True
    assert trends.severity_de_escalation is False

def test_trend_analyzer_confidence(engine, sample_entries):
    # a1 (0.7) -> a2 (0.8) -> a3 (0.6)
    for entry in sample_entries:
        engine._repository.add_entry(entry)
        
    trends = engine.analyze_trends("p1")
    # We compare a2 to a3 in ConfidenceTrendAnalyzer
    # curr = a3 (0.6), prev = a2 (0.8). difference = -0.2
    assert "Viral Infection" in trends.confidence_decreases
    assert trends.confidence_decreases["Viral Infection"] > 0

def test_generate_summary(engine, sample_entries):
    for entry in sample_entries:
        engine._repository.add_entry(entry)
        
    summary = engine.generate_summary("p1")
    assert "3 assessments recorded" in summary.overall_summary
    assert "improved from ROUTINE to HOME_CARE" in summary.severity_summary or "HOME_CARE" in summary.severity_summary
