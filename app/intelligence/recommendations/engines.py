from typing import List, Dict, Any
from app.intelligence.coordinator.models import ClinicalContext

class EmergencyRecommendationEngine:
    def generate(self, context: ClinicalContext) -> List[Dict[str, Any]]:
        return []

class MonitoringRecommendationEngine:
    def generate(self, context: ClinicalContext) -> List[Dict[str, Any]]:
        return [{"type": "monitoring", "text": "Monitor blood pressure daily."}]

class MedicationSafetyRecommendationEngine:
    def generate(self, context: ClinicalContext) -> List[Dict[str, Any]]:
        return []

class LifestyleRecommendationEngine:
    def generate(self, context: ClinicalContext) -> List[Dict[str, Any]]:
        return [{"type": "lifestyle", "text": "Maintain a low sodium diet."}]

class FollowupRecommendationEngine:
    def generate(self, context: ClinicalContext) -> List[Dict[str, Any]]:
        return []

class PreventiveRecommendationEngine:
    def generate(self, context: ClinicalContext) -> List[Dict[str, Any]]:
        return []
