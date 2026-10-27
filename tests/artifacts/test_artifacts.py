import pytest
from app.artifacts.orchestrator.pipeline_selector import PipelineSelector
from app.artifacts.orchestrator.artifact_orchestrator import ArtifactOrchestrator
from app.artifacts.artifact import MedicalArtifact
from app.terminology.normalizer import MedicalTerminologyNormalizer

def test_pipeline_selector():
    selector = PipelineSelector()
    
    art1 = MedicalArtifact(id="1", filename="CBC_Report.pdf")
    assert selector.select_pipeline(art1) == "LABORATORY_PIPELINE"
    
    art2 = MedicalArtifact(id="2", filename="chest_xray.png")
    assert selector.select_pipeline(art2) == "IMAGING_PIPELINE"
    
    art3 = MedicalArtifact(id="3", filename="prescription_2024.pdf")
    assert selector.select_pipeline(art3) == "MEDICATION_PIPELINE"

def test_artifact_orchestrator():
    orchestrator = ArtifactOrchestrator()
    art = MedicalArtifact(id="4", filename="lab.pdf")
    processed = orchestrator.process_artifact(art)
    
    assert processed.manifest.ocr == "COMPLETED"
    assert processed.manifest.status == "PROCESSED"
    assert processed.manifest.retrieval_ready is True

def test_terminology_normalizer():
    normalizer = MedicalTerminologyNormalizer()
    text = "take pcm for fever"
    normalized = normalizer.normalize(text)
    
    assert "Paracetamol" in normalized
    assert "pcm" not in normalized

def test_incremental_reprocessing():
    orchestrator = ArtifactOrchestrator()
    art = MedicalArtifact(id="5", filename="lab.pdf")
    art.manifest.ocr = "COMPLETED"
    
    processed = orchestrator.process_artifact(art)
    # The OCR shouldn't have changed, it should remain COMPLETED
    assert processed.manifest.ocr == "COMPLETED"
