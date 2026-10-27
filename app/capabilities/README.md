# AURA Capability OS

The Agent layer has been transformed into a Capability OS. This subsystem provides deterministic workflow routing using YAML definitions, strict typing for inter-capability contracts, and native parallel execution coordination.

## Core Flow
1. **Workflow Planner:** Reads intent and loads YAML definitions (e.g., `medication_review.yaml`).
2. **Execution Coordinator:** Translates YAML steps into parallel or sequential `asyncio` execution tasks wrapped with robust Retry and Timeout policies.
3. **Capabilities:** `AssessmentCapability`, `MedicationCapability`, etc. execute business logic. All capabilities strictly proxy LLM generation requests back to the central Orchestrator.

## Telemetry
Provides native timing for Critical Paths, Parallel Efficiency, and Retry Rates.
