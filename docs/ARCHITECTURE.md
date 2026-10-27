# AURA Architecture

## Overview

AURA is organized around deterministic clinical engines and an optional LLM explanation layer.

The backend is built with FastAPI. The frontend is built with React and Vite. Runtime state is stored in Redis when available, with an in-memory FakeRedis fallback for local development. Audit and reporting data are modeled for PostgreSQL through SQLAlchemy and Alembic.

## High-Level Architecture

```mermaid
flowchart TD
    Patient["Patient"] --> UI["React Patient UI"]
    UI --> API["FastAPI API"]

    API --> Session["Session Manager"]
    Session --> Redis["Redis or FakeRedis"]

    API --> Intake["Clinical Intake Engine"]
    Intake --> Evidence["Structured Clinical Evidence"]

    Evidence --> Reasoning["Clinical Reasoning Engine"]
    Reasoning --> Knowledge["Knowledge Repository"]
    Reasoning --> Matcher["Condition Matcher"]
    Reasoning --> Risk["Risk Factor Engine"]
    Reasoning --> Confidence["Confidence Engine"]

    Reasoning --> Interview["Adaptive Interview Engine"]
    Interview --> QuestionBank["Question Bank"]

    API --> RedFlags["Emergency Red Flag Detector"]
    API --> Severity["Severity Classifier"]
    Reasoning --> Explanation["Clinical Explanation Engine"]
    Severity --> OTC["OTC Safety Engine"]
    Severity --> Output["Triage Output Builder"]

    Severity --> Explanation
    Output --> LLM["Optional LLM Explanation"]
    Output --> Audit["Audit Logger"]
    Audit --> Database["PostgreSQL"]

    Output --> UI
```

## Request Flow

```mermaid
sequenceDiagram
    autonumber
    participant User as Patient
    participant UI as React Frontend
    participant API as FastAPI
    participant Session as Session Manager
    participant Intake as Intake Engine
    participant RedFlags as Red Flag Detector
    participant Severity as Severity Classifier
    participant Reasoning as Clinical Reasoning Engine
    participant LLM as LLM Orchestrator
    participant Output as Output Builder

    User->>UI: Start assessment
    UI->>API: POST /api/v1/session
    API->>Session: Create session
    Session-->>API: SessionState
    API-->>UI: session_id and expiry

    loop Intake questions
        UI->>API: GET /api/v1/session/question
        API->>Intake: Get next question
        Intake-->>API: IntakeQuestion
        API-->>UI: QuestionResponse
        User->>UI: Answer
        UI->>API: POST /api/v1/session/answer
        API->>Intake: Validate and update SessionState
        API->>Session: Persist updated state
    end

    API->>RedFlags: Evaluate emergency indicators
    API->>Severity: Classify severity
    API->>Reasoning: Evaluate deterministic clinical reasoning
    API->>LLM: Optional explanation only
    API->>Output: Assemble final patient output
    API-->>UI: Intake complete
    UI->>API: GET /api/v1/session/result
    API-->>UI: Final clinical output
```

## Adaptive Interview Flow

```mermaid
sequenceDiagram
    autonumber
    participant Evidence as Evidence Collector
    participant State as Interview State
    participant Reasoning as Clinical Reasoning Engine
    participant Interview as Adaptive Interview Engine
    participant Bank as Question Bank

    Evidence->>State: Add structured evidence
    Interview->>Evidence: Build updated ClinicalInput
    Interview->>Reasoning: Recalculate possible conditions
    Reasoning-->>Interview: ClinicalReasoningOutput
    Interview->>Interview: Calculate differential entropy
    Interview->>Interview: Check stopping criteria

    alt Interview complete
        Interview-->>State: Mark complete with reason
    else More information needed
        Interview->>Bank: Load unasked questions
        Bank-->>Interview: Candidate questions
        Interview->>Interview: Score expected information gain
        Interview-->>State: Select best next question
    end
```

## Clinical Reasoning Engine

Location: `app/reasoning/`

Responsibilities:

- Load structured clinical knowledge
- Match symptoms against condition definitions
- Apply demographic and chronic-condition risk factors
- Calculate normalized confidence scores
- Track supporting and conflicting evidence
- Report missing information
- Produce step-by-step reasoning traces

The reasoning engine is deterministic and does not call an LLM.

## Adaptive Clinical Interview Engine

Location: `app/interview/`

Responsibilities:

- Store structured clinical evidence
- Merge evidence into `ClinicalInput`
- Use reasoning output to estimate uncertainty
- Select high-value follow-up questions
- Stop when sufficient confidence, red flag interception, turn limits, or low information gain are reached

## Clinical Explanation Engine

Location: `app/explanation/`

Responsibilities:

- Transform `ClinicalReasoningOutput` into structured human-readable explanation
- Summarize leading possible condition without diagnosing
- Explain supporting and conflicting findings
- Explain deterministic risk factors
- Explain missing information
- Generate severity-based recommendations
- Generate safety notices and mandatory disclaimers
- Render Markdown, plain text, and structured JSON

The explanation engine is deterministic and does not call an LLM.

## API Surface

Current API routes are mounted under `/api/v1`:

- `POST /session` creates a session
- `GET /session/question` returns the next intake question
- `POST /session/answer` records an answer and may trigger triage
- `GET /session/result` returns the final triage output

The backend also exposes:

- `GET /health`

## Persistence

AURA currently models:

- `triage_sessions`
- `triage_audit_logs`

Redis is used for active session state. PostgreSQL is used for durable audit and reporting data.

## Safety Boundary

The output builder may include LLM-generated explanation text, but it must not allow LLM output to alter:

- Triage level
- Red flag outcomes
- Crisis resource injection
- Medication safety validation
- Final severity authority
