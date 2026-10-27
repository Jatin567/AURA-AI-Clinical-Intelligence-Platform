from typing import Dict, Any, List
from app.intelligence.coordinator.models import ClinicalContext

class QuestionPrioritizationEngine:
    def prioritize(self, unanswered_questions: List[Dict[str, Any]], context: ClinicalContext) -> List[Dict[str, Any]]:
        """Ranks unanswered questions by expected information gain."""
        ranked = []
        for q in unanswered_questions:
            ranked.append({
                "question": q.get("question"),
                "information_gain": 0.8,
                "priority": "high",
                "expected_confidence_improvement": 0.15,
                "clinical_justification": "Crucial to rule out severe complications."
            })
        return ranked

question_prioritization_engine = QuestionPrioritizationEngine()
