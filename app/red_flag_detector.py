import copy
from datetime import datetime, timezone
from typing import List, Optional, Any
from app.models.session import SessionState
from app.models.red_flag import RedFlagResult, RedFlagMatch, RedFlagSeverity


class RedFlagDetector:
    """
    Performs deterministic, rule-based evaluation of a medical session
    to detect emergency or urgent red flags.
    """

    def evaluate(self, session: SessionState) -> RedFlagResult:
        """
        Evaluates the session against all rules and returns a RedFlagResult.
        Guaranteed not to raise an exception.
        """
        try:
            # 1. Capture input snapshot first
            input_snapshot = {
                "chief_complaint": session.chief_complaint,
                "symptom_duration": session.symptom_duration,
                "symptom_severity": session.symptom_severity,
                "symptoms": session.symptoms.copy() if session.symptoms else [],
                "patient_profile": session.patient_profile.model_dump() if session.patient_profile else {}
            }

            # 2. Collect all rules
            rules = [
                self._check_chest_pain,
                self._check_breathing,
                self._check_stroke_signs,
                self._check_loss_of_consciousness,
                self._check_severe_bleeding,
                self._check_infant_fever,
                self._check_high_severity,
                self._check_mental_health_crisis
            ]

            matches: List[RedFlagMatch] = []
            for rule in rules:
                match = rule(session)
                if match:
                    matches.append(match)

            # 3. Determine highest severity
            highest = None
            if any(m.severity == RedFlagSeverity.EMERGENCY for m in matches):
                highest = RedFlagSeverity.EMERGENCY
            elif any(m.severity == RedFlagSeverity.URGENT for m in matches):
                highest = RedFlagSeverity.URGENT

            return RedFlagResult(
                evaluated_at=datetime.now(timezone.utc),
                flags_matched=matches,
                highest_severity=highest,
                input_snapshot=input_snapshot
            )

        except Exception as e:
            # Fallback if anything goes wrong
            return RedFlagResult(
                evaluated_at=datetime.now(timezone.utc),
                flags_matched=[],
                highest_severity=None,
                input_snapshot={},
                evaluation_error=str(e)
            )

    def _matches_substring(self, session: SessionState, keywords: List[str]) -> Optional[str]:
        """Helper to check both chief_complaint and symptoms for keyword substrings."""
        # Normalize chief_complaint
        cc = (session.chief_complaint or "").lower()
        for kw in keywords:
            if kw.lower() in cc:
                return session.chief_complaint

        # Normalize symptoms list
        for s in (session.symptoms or []):
            s_low = s.lower()
            for kw in keywords:
                if kw.lower() in s_low:
                    return s
        
        return None

    def _check_chest_pain(self, session: SessionState) -> Optional[RedFlagMatch]:
        keywords = ["chest pain", "chest tightness", "chest pressure"]
        matched_on = self._matches_substring(session, keywords)
        if matched_on:
            return RedFlagMatch(
                rule_id="chest_pain",
                severity=RedFlagSeverity.EMERGENCY,
                matched_on=matched_on,
                explanation="You are reporting chest pain or pressure. This requires immediate emergency medical evaluation.",
                rule_description="Triggers on 'chest pain', 'chest tightness', or 'chest pressure'."
            )
        return None

    def _check_breathing(self, session: SessionState) -> Optional[RedFlagMatch]:
        keywords = ["difficulty breathing", "shortness of breath", "can't breathe", "breathing problems"]
        matched_on = self._matches_substring(session, keywords)
        if matched_on:
            return RedFlagMatch(
                rule_id="breathing_difficulty",
                severity=RedFlagSeverity.EMERGENCY,
                matched_on=matched_on,
                explanation="You are reporting difficulty breathing. This requires immediate emergency medical evaluation.",
                rule_description="Triggers on 'difficulty breathing', 'shortness of breath', 'can't breathe', or 'breathing problems'."
            )
        return None

    def _check_stroke_signs(self, session: SessionState) -> Optional[RedFlagMatch]:
        keywords = [
            "facial drooping", "arm weakness", "speech difficulty", 
            "sudden confusion", "sudden vision loss", 
            "worst headache", "thunderclap headache"
        ]
        matched_on = self._matches_substring(session, keywords)
        if matched_on:
            return RedFlagMatch(
                rule_id="stroke_signs",
                severity=RedFlagSeverity.EMERGENCY,
                matched_on=matched_on,
                explanation="You are reporting signs that could indicate a stroke or severe neurological issue. This is an emergency.",
                rule_description="Triggers on signs like facial drooping, arm weakness, speech difficulty, etc."
            )
        return None

    def _check_loss_of_consciousness(self, session: SessionState) -> Optional[RedFlagMatch]:
        keywords = ["loss of consciousness", "fainted", "passed out", "unresponsive"]
        matched_on = self._matches_substring(session, keywords)
        if matched_on:
            return RedFlagMatch(
                rule_id="loss_of_consciousness",
                severity=RedFlagSeverity.EMERGENCY,
                matched_on=matched_on,
                explanation="You are reporting a loss of consciousness or fainting. This requires immediate emergency evaluation.",
                rule_description="Triggers on 'loss of consciousness', 'fainted', 'passed out', or 'unresponsive'."
            )
        return None

    def _check_severe_bleeding(self, session: SessionState) -> Optional[RedFlagMatch]:
        keywords = ["uncontrolled bleeding", "heavy bleeding", "bleeding won't stop"]
        matched_on = self._matches_substring(session, keywords)
        if matched_on:
            return RedFlagMatch(
                rule_id="severe_bleeding",
                severity=RedFlagSeverity.EMERGENCY,
                matched_on=matched_on,
                explanation="You are reporting severe or uncontrolled bleeding. This requires immediate emergency evaluation.",
                rule_description="Triggers on 'uncontrolled bleeding', 'heavy bleeding', or 'bleeding won't stop'."
            )
        return None

    def _check_infant_fever(self, session: SessionState) -> Optional[RedFlagMatch]:
        # Check if confirmed infant under 3 months via is_infant flag
        is_infant = session.patient_profile.is_infant if session.patient_profile else False
        if is_infant:
            keywords = ["fever"]
            matched_on = self._matches_substring(session, keywords)
            if matched_on:
                return RedFlagMatch(
                    rule_id="infant_fever",
                    severity=RedFlagSeverity.EMERGENCY,
                    matched_on=matched_on,
                    explanation="Fever in an infant under 3 months old is a medical emergency.",
                    rule_description="Triggers when is_infant is True AND 'fever' is mentioned."
                )
        return None

    def _check_high_severity(self, session: SessionState) -> Optional[RedFlagMatch]:
        # NOTE: This rule produces URGENT, not EMERGENCY. Severity is self-reported and subjective;
        # a 9/10 score from one patient may not be equivalent to another. This is a soft signal
        # that must be evaluated alongside other clinical red flags in the final triage output.
        severity = session.symptom_severity
        if severity is not None and severity >= 9:
            return RedFlagMatch(
                rule_id="high_severity_score",
                severity=RedFlagSeverity.URGENT,
                matched_on=str(severity),
                explanation=f"You have reported a high symptom severity score of {severity}/10. This requires urgent evaluation.",
                rule_description="Triggers when symptom_severity >= 9."
            )
        return None

    def _check_mental_health_crisis(self, session: SessionState) -> Optional[RedFlagMatch]:
        keywords = ["suicidal", "want to die", "self harm", "overdose"]
        matched_on = self._matches_substring(session, keywords)
        if matched_on:
            return RedFlagMatch(
                rule_id="mental_health_crisis",
                severity=RedFlagSeverity.EMERGENCY,
                matched_on=matched_on,
                explanation="You are reporting a mental health crisis. Please call a crisis hotline or seek emergency help immediately.",
                rule_description="Triggers on 'suicidal', 'want to die', 'self harm', or 'overdose'.",
                requires_immediate_crisis_resource=True
            )
        return None
