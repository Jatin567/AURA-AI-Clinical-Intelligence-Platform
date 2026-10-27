import sys
from datetime import datetime, timezone
from typing import List
from app.models.session import SessionState
from app.models.triage import TriageLevel
from app.models.llm import OrchestratorResult
from app.models.otc import OTCResult
from app.models.output import TriageOutput

class TriageOutputBuilder:
    """
    Final assembly module for patient-facing triage output.
    Applies safety gates, static fallbacks, and crisis resource injection.
    """

    LABEL_MAP = {
        TriageLevel.EMERGENCY: "Seek Emergency Care Immediately — Call 911",
        TriageLevel.URGENT: "See a Doctor Within 24 Hours",
        TriageLevel.ROUTINE: "Schedule a Doctor Appointment",
        TriageLevel.HOME_CARE: "You Can Manage This at Home"
    }

    STATIC_EXPLANATIONS = {
        TriageLevel.EMERGENCY: (
            "Based on your reported symptoms, you require immediate emergency medical attention. "
            "Please call 911 or go to the nearest emergency room now. Do not drive yourself."
        ),
        TriageLevel.URGENT: "Your symptoms require a prompt medical evaluation. Please see a doctor or visit an urgent care clinic today.",
        TriageLevel.ROUTINE: "Your symptoms should be evaluated by a healthcare professional. Please schedule an appointment with your doctor.",
        TriageLevel.HOME_CARE: "Based on your reported symptoms, you may be able to manage your care at home. Monitor your symptoms closely."
    }

    ACTION_ITEMS_MAP = {
        TriageLevel.EMERGENCY: ["Call 911 immediately", "Do not eat or drink anything", "Stay calm and wait for help"],
        TriageLevel.URGENT: ["Contact your doctor or urgent care today", "Monitor your symptoms closely", "If symptoms worsen, go to the ER"],
        TriageLevel.ROUTINE: ["Schedule an appointment with your doctor", "Keep a symptom diary", "Return here if symptoms worsen"],
        TriageLevel.HOME_CARE: ["Rest and stay hydrated", "Monitor your symptoms", "Return here if symptoms worsen or new symptoms develop"]
    }

    MEDICAL_DISCLAIMER = (
        "AURA is an AI-powered triage assistant and does not provide medical diagnoses. "
        "Always consult a qualified healthcare professional for medical advice, diagnosis, or treatment. "
        "In case of emergency, call 911."
    )

    CRISIS_RESOURCE_US = (
        "If you are in crisis, please call or text 988 (Suicide & Crisis Lifeline) immediately. "
        "You can also text HOME to 741741 (Crisis Text Line)."
    )

    CRISIS_RESOURCE_INTL = (
        "If you are in crisis, please contact your local emergency services or the "
        "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/"
    )

    def build(self, session: SessionState, orchestrator_result: OrchestratorResult, 
              otc_result: OTCResult, user_region: str = "US") -> TriageOutput:
        """
        Assembles all internal results into the final TriageOutput.
        Guaranteed not to raise an exception.
        """
        try:
            decision = orchestrator_result.triage_decision
            level = decision.triage_level

            # 1. Triage Label
            triage_label = self.LABEL_MAP.get(level, "Unknown Triage Level")

            # 2. Explanation Assembly
            explanation = self._assemble_explanation(orchestrator_result, level)

            # 3. Crisis Resources (Absolute Injection)
            crisis_resources = self._inject_crisis_resources(decision, user_region)

            # 4. OTC Suggestions
            approved_otcs = []
            otc_disclaimers = []
            for suggestion in otc_result.suggestions:
                if suggestion.approved:
                    med = suggestion.medicine
                    common_names = ", ".join(med.common_names)
                    approved_otcs.append(f"{med.name} ({common_names}) — {med.standard_disclaimer}")
                    if med.standard_disclaimer not in otc_disclaimers:
                        otc_disclaimers.append(med.standard_disclaimer)

            # 5. Action Items
            action_items = self.ACTION_ITEMS_MAP.get(level, [])

            return TriageOutput(
                session_id=session.session_id,
                triage_level=level,
                triage_label=triage_label,
                explanation=explanation,
                approved_otc_suggestions=approved_otcs,
                otc_disclaimers=otc_disclaimers,
                action_items=action_items,
                crisis_resources=crisis_resources,
                medical_disclaimer=self.MEDICAL_DISCLAIMER,
                assembled_at=datetime.now(timezone.utc),
                llm_was_used=not orchestrator_result.llm_skipped
            )

        except Exception as e:
            sys.stderr.write(f"CRITICAL ERROR in TriageOutputBuilder: {str(e)}\n")
            # Safe fallback output
            return TriageOutput(
                session_id=session.session_id,
                triage_level=TriageLevel.URGENT,
                triage_label=self.LABEL_MAP[TriageLevel.URGENT],
                explanation="An internal error occurred during result assembly. Please proceed with URGENT care as a safety precaution.",
                approved_otc_suggestions=[],
                otc_disclaimers=[],
                action_items=self.ACTION_ITEMS_MAP[TriageLevel.URGENT],
                crisis_resources=[],
                medical_disclaimer=self.MEDICAL_DISCLAIMER,
                assembled_at=datetime.now(timezone.utc),
                llm_was_used=False
            )

    def _assemble_explanation(self, orchestrator_result: OrchestratorResult, level: TriageLevel) -> str:
        # LLM Skipped (EMERGENCY or otherwise)
        if orchestrator_result.llm_skipped:
            return self.STATIC_EXPLANATIONS.get(level, "No explanation available.")

        # LLM Failed (Generation Error)
        if orchestrator_result.llm_response and orchestrator_result.llm_response.generation_error:
            return self.STATIC_EXPLANATIONS.get(level, "No explanation available.")

        # Success - Use LLM text
        if orchestrator_result.llm_response and orchestrator_result.llm_response.explanation:
            return orchestrator_result.llm_response.explanation

        return self.STATIC_EXPLANATIONS.get(level, "No explanation available.")

    def _inject_crisis_resources(self, decision, user_region: str) -> List[str]:
        # Unconditional injection if flag is set
        resources = []
        red_flag_result = decision.red_flag_result
        if red_flag_result and red_flag_result.flags_matched:
            for match in red_flag_result.flags_matched:
                if getattr(match, 'requires_immediate_crisis_resource', False):
                    text = self.CRISIS_RESOURCE_US if user_region == "US" else self.CRISIS_RESOURCE_INTL
                    if text not in resources:
                        resources.append(text)
        return resources
