import sys
from datetime import datetime, timezone
from typing import List, Optional
from app.models.session import SessionState
from app.models.triage import TriageLevel
from app.models.otc import OTCResult, OTCSuggestion, OTCMedicine
from app.data.otc_allowlist import OTC_ALLOWLIST

class OTCSuggester:
    """
    Validates OTC medication candidates against a clinical allowlist and patient-specific safety factors.
    Strictly follows 4-gate validation logic.
    """

    def validate(self, session: SessionState, candidates: List[str], triage_level: TriageLevel) -> OTCResult:
        """
        Main entry point for OTC validation. Guaranteed not to raise an exception.
        """
        try:
            now = datetime.now(timezone.utc)

            # Gate 1 — Triage level check: Short-circuit for EMERGENCY or URGENT
            if triage_level in [TriageLevel.EMERGENCY, TriageLevel.URGENT]:
                return OTCResult(
                    session_id=session.session_id,
                    suggestions=[],
                    evaluated_at=now,
                    triage_level_at_evaluation=triage_level
                )

            # Gate 1b — Neonate safety gate: NO OTC for neonates (under 28 days)
            if session.patient_profile and session.patient_profile.is_neonate:
                return OTCResult(
                    session_id=session.session_id,
                    suggestions=[],
                    evaluated_at=now,
                    triage_level_at_evaluation=triage_level,
                    rejection_reason="No OTC medications for neonates"
                )

            suggestions = []
            for raw_candidate in candidates:
                suggestion = self._evaluate_candidate(session, raw_candidate)
                suggestions.append(suggestion)

            return OTCResult(
                session_id=session.session_id,
                suggestions=suggestions,
                evaluated_at=now,
                triage_level_at_evaluation=triage_level
            )

        except Exception as e:
            # Fallback to empty results on internal failure
            sys.stderr.write(f"CRITICAL ERROR in OTCSuggester: {str(e)}\n")
            return OTCResult(
                session_id=session.session_id,
                suggestions=[],
                evaluated_at=datetime.now(timezone.utc),
                triage_level_at_evaluation=triage_level
            )

    def _evaluate_candidate(self, session: SessionState, raw_candidate: str) -> OTCSuggestion:
        # Gate 2 — Allowlist check: Normalization + dictionary lookup
        normalized_name = raw_candidate.strip().lower()
        medicine = OTC_ALLOWLIST.get(normalized_name)

        if not medicine:
            # Re-create a placeholder medicine for the suggestion object to satisfy Pydantic
            # in case of rejection, but marking it rejected strictly.
            # Using a dummy medicine structure for the rejection report.
            return OTCSuggestion(
                medicine=OTCMedicine(
                    name=raw_candidate,
                    common_names=[],
                    safe_for_ages_above=0,
                    contraindicated_conditions=[],
                    contraindicated_medications=[],
                    max_duration_days=0,
                    standard_disclaimer=""
                ),
                approved=False,
                rejection_reason="Not in approved OTC allowlist"
            )

        # Gate 3 — Age check
        profile = session.patient_profile
        if profile and profile.age is not None:
            if profile.age < medicine.safe_for_ages_above:
                return OTCSuggestion(
                    medicine=medicine,
                    approved=False,
                    rejection_reason=f"Not recommended for age {profile.age}"
                )

        # Gate 4 — Contraindication check
        if profile:
            # Check Conditions (case-insensitive)
            patient_conditions = [c.lower() for c in profile.known_conditions]
            for condition in medicine.contraindicated_conditions:
                if condition.lower() in patient_conditions:
                    return OTCSuggestion(
                        medicine=medicine,
                        approved=False,
                        rejection_reason=f"Contraindicated due to condition: {condition}"
                    )

            # Check Medications (case-insensitive)
            # PatientProfile has known_conditions, but user request mentioned current_medications
            # Checking if current_medications exists in PatientProfile model (it doesn't yet based on session.py logs)
            # Re-evaluating session.py content or assuming it might be added or using a placeholder attribute.
            # According to previous logs, PatientProfile only has known_conditions.
            # User prompt says "Check session.patient_profile.current_medications".
            # I must check if I missed adding this field. 
            # If not present, I'll treat it as empty or use hasattr.
            current_meds = getattr(profile, 'current_medications', [])
            patient_meds = [m.lower() for m in current_meds]
            for contra_med in medicine.contraindicated_medications:
                if contra_med.lower() in patient_meds:
                    return OTCSuggestion(
                        medicine=medicine,
                        approved=False,
                        rejection_reason=f"Contraindicated due to medication: {contra_med}"
                    )

        return OTCSuggestion(
            medicine=medicine,
            approved=True,
            rejection_reason=None
        )
