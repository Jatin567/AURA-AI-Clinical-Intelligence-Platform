# Contributing to AURA

Thank you for contributing to AURA.

AURA is a clinical decision support project, so safety and explainability matter more than speed.

## Core Rules

- Do not move medical decision-making into the LLM.
- Do not allow the LLM to determine emergencies, severity, red flags, or medication safety.
- Preserve existing APIs unless a migration plan is documented.
- Keep clinical logic deterministic, testable, and explainable.
- Prefer structured data repositories over hardcoded disease logic.
- Add or update tests for safety-sensitive behavior.
- Update documentation when architecture, setup, API behavior, or safety boundaries change.

## Development Workflow

1. Read the project brief and architecture docs.
2. Keep changes scoped to one concern.
3. Add or update unit tests.
4. Run the relevant test suite.
5. Update documentation if behavior or setup changes.

## Testing Expectations

Run focused tests for the area you changed:

```powershell
pytest tests/test_reasoning_engine.py
pytest tests/test_red_flag_detector.py
pytest tests/test_severity_classifier.py
pytest tests/test_safety_fixes.py
```

Run the full suite before larger changes:

```powershell
pytest
```

## Safety-Sensitive Changes

Safety-sensitive changes include:

- Red flag rules
- Severity classification
- Clinical reasoning
- Risk factor weighting
- OTC recommendations
- Crisis resources
- LLM prompt constraints
- Output assembly

These changes require explicit tests and clear documentation.

## Documentation Standards

Documentation should be:

- Accurate to current code
- Honest about limitations
- Clear about safety boundaries
- Useful to new contributors
- Written in plain language

## Medical Disclaimer

AURA does not diagnose patients and does not replace professional medical care. Contributors should avoid claims that imply clinical autonomy, diagnosis, prescription, or guaranteed medical accuracy.

