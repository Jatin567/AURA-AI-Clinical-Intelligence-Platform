# AURA Multimodal Artifact Pipeline

The `app/artifacts` subsystem is the enterprise-grade ingestion engine for all user uploads. 
It prevents raw, noisy OCR texts from directly entering the Orchestrator.

## Core Features
- **Artifact Orchestrator**: Uses the `PipelineSelector` to deterministically route documents. "CBC.pdf" goes exclusively to the Lab Pipeline.
- **Incremental Reprocessing**: The `ArtifactManifest` tracks the state of each extraction phase (OCR, Classifier, Entities). Re-running a document bypasses heavy OCR if it's already "COMPLETED".
- **Medical Terminology Normalizer**: Intercepts OCR text like "PCM" and canonicalizes it to "Paracetamol" before downstream extraction.
- **Vision Engine**: Provides physical image metadata (orientation, quality, size) for early validation.

## Deep Extraction and UI
Every extracted artifact is packaged with a strict `Confidence Score` and physical bounding box. These mapped `EvidencePackages` are streamed to the frontend via rich UI components like `PrescriptionCard` and `LabCard`.
