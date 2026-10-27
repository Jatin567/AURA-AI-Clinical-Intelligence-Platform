from datetime import datetime, timezone
from typing import Optional
from app.models.session import SessionState
from app.models.red_flag import RedFlagResult, RedFlagSeverity
from app.models.triage import TriageLevel, TriageDecision


class SeverityClassifier:
    """
    Classifies the severity of a session based on red flags and symptom profile.
    Deterministic, rule-based logic with strict priority.
    """

    VERSION = "1.0"

    def classify(self, session: SessionState, red_flag_result: RedFlagResult) -> TriageDecision:
        """
        Main entry point for classification. Guaranteed not to raise an exception.
        """
        try:
            # Rule 1 — EMERGENCY (hard gate)
            # Short-circuit: if red_flag_result.highest_severity == EMERGENCY, return EMERGENCY immediately.
            if red_flag_result.highest_severity == RedFlagSeverity.EMERGENCY:
                # Find the first EMERGENCY match for the reason
                primary_match = next(m for m in red_flag_result.flags_matched if m.severity == RedFlagSeverity.EMERGENCY)
                return self._build_decision(
                    session_id=session.session_id,
                    level=TriageLevel.EMERGENCY,
                    confidence="high",
                    reason=primary_match.explanation,
                    factors=[m.explanation for m in red_flag_result.flags_matched],
                    red_flag_result=red_flag_result
                )

            # Rule 2 — URGENT (from red flags)
            # If red_flag_result.highest_severity == URGENT, return URGENT.
            if red_flag_result.highest_severity == RedFlagSeverity.URGENT:
                urgent_matches = [m for m in red_flag_result.flags_matched if m.severity == RedFlagSeverity.URGENT]
                return self._build_decision(
                    session_id=session.session_id,
                    level=TriageLevel.URGENT,
                    confidence="high",
                    reason="Based on clinical red flags identified during intake.",
                    factors=[m.explanation for m in urgent_matches],
                    red_flag_result=red_flag_result
                )

            # Rule 3 — URGENT (from symptom profile: severity >= 7 AND acute onset)
            if self._is_acute_high_severity(session):
                return self._build_decision(
                    session_id=session.session_id,
                    level=TriageLevel.URGENT,
                    confidence="medium",
                    reason="High symptom severity with acute onset reported.",
                    factors=["Reported severity >= 7", "Acute onset duration keywords matched"],
                    red_flag_result=red_flag_result
                )

            # Rule 4 — URGENT (known condition interaction: conditions non-empty AND severity >= 6)
            if (session.patient_profile and session.patient_profile.known_conditions and 
                session.symptom_severity is not None and session.symptom_severity >= 6):
                conditions = ", ".join(session.patient_profile.known_conditions)
                return self._build_decision(
                    session_id=session.session_id,
                    level=TriageLevel.URGENT,
                    confidence="medium",
                    reason=f"Significant symptom severity in a patient with known conditions: {conditions}.",
                    factors=[f"Known conditions: {conditions}", f"Reported severity: {session.symptom_severity}"],
                    red_flag_result=red_flag_result
                )

            # Rule 5 — ROUTINE: severity 4-6 OR duration keywords ("days", "week", "weeks")
            if self._is_routine(session):
                return self._build_decision(
                    session_id=session.session_id,
                    level=TriageLevel.ROUTINE,
                    confidence="medium",
                    reason="Moderate symptoms or chronic duration reported.",
                    factors=self._get_routine_factors(session),
                    red_flag_result=red_flag_result
                )

            # Rule 6 — HOME_CARE (default)
            confidence = "low" if session.symptom_severity is None else "medium"
            return self._build_decision(
                session_id=session.session_id,
                level=TriageLevel.HOME_CARE,
                confidence=confidence,
                reason="Symptoms appear mild and do not meet clinical escalation thresholds.",
                factors=["Baseline monitoring recommended"],
                red_flag_result=red_flag_result
            )

        except Exception as e:
            # Fallback to URGENT for safety. Ensure red_flag_result is valid for Pydantic.
            fallback_rf = red_flag_result if isinstance(red_flag_result, RedFlagResult) else RedFlagResult(
                evaluated_at=datetime.now(timezone.utc),
                flags_matched=[],
                highest_severity=None,
                input_snapshot={}
            )
            return TriageDecision(
                session_id=session.session_id,
                triage_level=TriageLevel.URGENT,
                confidence="low",
                primary_reason="Classification error — defaulting to URGENT for safety",
                contributing_factors=[str(e)],
                red_flag_result=fallback_rf,
                classified_at=datetime.now(timezone.utc),
                classification_version=self.VERSION
            )

    def _build_decision(self, session_id: str, level: TriageLevel, confidence: str, 
                        reason: str, factors: list[str], red_flag_result: RedFlagResult) -> TriageDecision:
        return TriageDecision(
            session_id=session_id,
            triage_level=level,
            confidence=confidence,
            primary_reason=reason,
            contributing_factors=factors,
            red_flag_result=red_flag_result,
            classified_at=datetime.now(timezone.utc),
            classification_version=self.VERSION
        )

    def _is_acute_high_severity(self, session: SessionState) -> bool:
        if session.symptom_severity is None or session.symptom_severity < 7:
            return False
        
        # FIX 2: Match against chief_complaint (verbatim patient text) for acute onset
        text_to_search = (session.chief_complaint or "").lower()
        acute_keywords = ["sudden", "hours", "today", "this morning", "suddenly"]
        return any(kw in text_to_search for kw in acute_keywords)

    def _is_routine(self, session: SessionState) -> bool:
        # severity between 4-6 inclusive
        if session.symptom_severity is not None and 4 <= session.symptom_severity <= 6:
            return True
        
        # duration contains ("days", "week", "weeks")
        duration = (session.symptom_duration or "").lower()
        chronic_keywords = ["days", "week", "weeks"]
        return any(kw in duration for kw in chronic_keywords)

    def _get_routine_factors(self, session: SessionState) -> list[str]:
        factors = []
        if session.symptom_severity is not None and 4 <= session.symptom_severity <= 6:
            factors.append(f"Moderate severity reported: {session.symptom_severity}")
        
        duration = (session.symptom_duration or "").lower()
        chronic_keywords = ["days", "week", "weeks"]
        matches = [kw for kw in chronic_keywords if kw in duration]
        if matches:
            factors.append(f"Symptoms persistent for: {', '.join(matches)}")
        
        return factors
