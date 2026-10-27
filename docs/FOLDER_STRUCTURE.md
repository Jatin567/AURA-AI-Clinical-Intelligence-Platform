# Folder Structure

## Root

```text
AURA/
  .env.example
  alembic/
  app/
  datasets/
  docs/
  frontend/
  logs/
  tests/
```

## Backend

```text
app/
  api/
    routes.py
    schemas.py
  data/
    otc_allowlist.py
  db/
    database.py
    models.py
  explanation/
    __init__.py
    disclaimer_engine.py
    explanation_engine.py
    explanation_templates.py
    formatter.py
    models.py
    recommendation_engine.py
    README.md
  interview/
    adaptive_engine.py
    evidence_collector.py
    models.py
    question_bank.py
    data/question_bank.json
  models/
    intake.py
    llm.py
    otc.py
    output.py
    red_flag.py
    session.py
    triage.py
  reasoning/
    condition_matcher.py
    confidence_engine.py
    knowledge_repository.py
    models.py
    reasoning_engine.py
    risk_factor_engine.py
    data/clinical_knowledge.json
  audit_logger.py
  config.py
  dependencies.py
  intake_engine.py
  llm_orchestrator.py
  main.py
  otc_suggester.py
  red_flag_detector.py
  session_manager.py
  severity_classifier.py
  triage_output_builder.py
```

## Frontend

```text
frontend/
  index.html
  package.json
  vite.config.js
  src/
    App.jsx
    App.css
    index.css
    main.jsx
    assets/
    components/
    context/
    hooks/
    screens/
```

## Tests

```text
tests/
  test_adaptive_interview_engine.py
  test_api.py
  test_audit_logger.py
  test_db_models.py
  test_explanation_engine.py
  test_intake_engine.py
  test_llm_orchestrator.py
  test_otc_suggester.py
  test_reasoning_engine.py
  test_red_flag_detector.py
  test_safety_fixes.py
  test_session_manager.py
  test_severity_classifier.py
  test_triage_output_builder.py
```

## Documentation Ownership

- `README.md` is the public entry point.
- `docs/PROJECT_BRIEF.md` explains product vision and principles.
- `docs/ARCHITECTURE.md` explains technical design and flows.
- `docs/ROADMAP.md` tracks planned milestones.
- `docs/SETUP.md` explains local development.
- `docs/DEPLOYMENT.md` explains production deployment expectations.
- `docs/FOLDER_STRUCTURE.md` documents repository organization.
- `docs/assets/` stores screenshots, GIFs, and demo media.
