import logging
from app.artifacts.artifact import MedicalArtifact
from app.artifacts.orchestrator.pipeline_selector import PipelineSelector

logger = logging.getLogger(__name__)

class ArtifactOrchestrator:
    def __init__(self):
        self.selector = PipelineSelector()

    def process_artifact(self, artifact: MedicalArtifact):
        pipeline = self.selector.select_pipeline(artifact)
        logger.info(f"Routing {artifact.filename} to {pipeline}")
        
        # Stub incremental processing logic
        if artifact.manifest.ocr == "COMPLETED":
            logger.info("OCR already completed, skipping...")
        else:
            artifact.manifest.ocr = "COMPLETED"
            
        artifact.manifest.classifier = "COMPLETED"
        artifact.manifest.retrieval_ready = True
        artifact.manifest.status = "PROCESSED"
        
        return artifact
