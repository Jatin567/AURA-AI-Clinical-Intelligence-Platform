from app.artifacts.artifact import MedicalArtifact

class PipelineSelector:
    """Determines which processing pipeline an artifact requires."""
    
    def select_pipeline(self, artifact: MedicalArtifact) -> str:
        filename = artifact.filename.lower()
        if "lab" in filename or "cbc" in filename:
            return "LABORATORY_PIPELINE"
        elif "prescription" in filename or "rx" in filename:
            return "MEDICATION_PIPELINE"
        elif "xray" in filename or "mri" in filename:
            return "IMAGING_PIPELINE"
        elif "ecg" in filename:
            return "ECG_PIPELINE"
        else:
            return "DOCUMENT_PIPELINE"
