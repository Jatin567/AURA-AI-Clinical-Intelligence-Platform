from typing import Dict, Any, List

class ExplainabilityEngine:
    def explain(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Appends the mandatory 7-point explanation structure."""
        recommendation["explanation"] = {
            "why": "Derived from deterministic guideline matching.",
            "supporting_evidence": ["Evidence reference 1"],
            "guideline_references": ["Guideline X"],
            "confidence_modifiers": {"positive": ["Strong symptom match"], "negative": ["Missing lab results"]},
            "missing_information": ["Recent blood pressure reading"],
            "alternative_considerations": ["Consider specialist referral if symptoms persist."],
            "recommended_next_action": "Schedule follow-up in 2 weeks."
        }
        return recommendation

explainability_engine = ExplainabilityEngine()
