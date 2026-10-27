# AURA Roadmap

## v1.0 Documentation and Stabilization

Goal: make AURA understandable, demoable, and maintainable.

Deliverables:

- Professional README
- Project brief
- Architecture documentation
- Setup guide
- Deployment guide
- Contributing guide
- Folder structure documentation
- Architecture diagrams
- Sequence diagrams
- Demo media placeholders
- Safety and LLM boundary documentation

## v1.0 Product Milestone

Goal: complete the core clinical decision support experience.

Focus areas:

- Polish clinical reasoning engine
- Polish adaptive interview engine
- Strengthen emergency red flag coverage
- Expand test coverage for safety-sensitive paths
- Improve patient-facing result clarity
- Document known limitations
- Add a reproducible dependency file
- Add production deployment configuration

## v2.0 Clinical Explanation Engine

Extend the deterministic explanation layer that transforms reasoning output into structured explanation objects before optional LLM rewriting.

Expected outputs:

- Supporting evidence
- Conflicting evidence
- Risk factors
- Confidence explanation
- Missing information summary
- Next-step rationale

## v2.0 Clinical Report Generator

Generate downloadable reports containing:

- Chief complaint
- Symptoms
- Evidence collected
- Differential candidates
- Confidence scores
- Risk factors
- Reasoning summary
- Recommended action
- Medical disclaimer

## v2.0 Patient Timeline

Track symptom progression over time.

Potential features:

- Symptom onset
- Severity changes
- Intervention history
- Follow-up status
- Exportable timeline

## v2.0 Lab Report Interpreter

Interpret common laboratory reports using deterministic rules and explainable clinical references.

Potential inputs:

- Manual lab values
- Uploaded PDFs
- OCR-derived structured values

## v2.0 Medication Safety Engine

Check:

- Allergy conflicts
- Contraindications
- Drug interactions
- Age-specific cautions
- Chronic condition cautions

## v2.0 Doctor Dashboard

Allow clinicians to review:

- Patient interviews
- Reasoning outputs
- Reports
- Timelines
- Audit logs

## Production Platform

Long-term infrastructure goals:

- Containerized deployment
- Managed PostgreSQL
- Managed Redis
- Observability and alerting
- Privacy-conscious analytics
- Security review
- Public documentation site
- Open-source contribution workflow
