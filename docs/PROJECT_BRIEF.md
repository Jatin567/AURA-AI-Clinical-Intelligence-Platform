# AURA v1.0 Project Brief

## Vision

AURA is an AI-powered Clinical Decision Support Platform.

It is not a chatbot and not a diagnosis tool. It helps patients complete structured clinical intake, detects emergency red flags, performs deterministic clinical reasoning, and generates explainable medical guidance.

Patient safety is the highest priority.

## Core Principle

The LLM never makes medical decisions.

Deterministic engines are responsible for:

- Emergency detection
- Red flag detection
- Severity classification
- Clinical reasoning
- OTC medication safety

The LLM may only explain deterministic results in patient-friendly language.

## Long-Term Goal

AURA is intended to become:

- A production-quality open-source project
- A flagship portfolio project
- A strong technical interview centerpiece
- A real product capable of supporting thousands of active users
- A demonstration of AI integration, explainable reasoning, and modular backend architecture

## Engineering Principles

### Patient Safety First

Emergency logic must be deterministic, testable, and auditable.

The system must not allow an LLM to determine emergencies, severity, red flags, or medication safety.

### Explainable AI

Every clinical output should explain:

- Why the recommendation was made
- Which evidence supported it
- Which evidence conflicted with it
- Which risk factors mattered
- How confidence was calculated

### Modular Architecture

Each subsystem should own one responsibility and communicate through explicit models.

Avoid tight coupling between intake, reasoning, severity, red flags, OTC validation, persistence, and explanation.

### Data-Driven Design

Medical knowledge should live in structured repositories such as JSON data files or future database-backed knowledge stores.

Business logic should consume this knowledge, not hardcode disease definitions directly into algorithms.

### Production Quality

Each meaningful feature should include:

- Unit tests
- Documentation
- Clear models
- Failure handling
- Extensibility
- Safety constraints

## Current Product Shape

AURA currently includes:

- Structured intake flow
- Session lifecycle management
- Emergency red flag evaluation
- Severity classification
- Deterministic clinical reasoning
- Adaptive interview question selection
- OTC recommendation safety gates
- LLM explanation orchestration
- Audit logging
- PostgreSQL persistence models
- React patient-facing frontend

## Authoritative Severity Levels

The current code uses:

- `EMERGENCY`
- `URGENT`
- `ROUTINE`
- `HOME_CARE`

Future roadmap language may introduce names such as `NON_URGENT`, but any severity taxonomy change should be treated as an API and product decision.

## Success Criteria for v1.0

AURA v1.0 should be:

- Safe enough to demo responsibly
- Clear enough for outside contributors to understand
- Documented enough for technical reviewers
- Modular enough to extend
- Tested enough to trust core clinical behavior
- Honest about limitations and medical boundaries

