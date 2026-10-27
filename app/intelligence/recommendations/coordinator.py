from typing import List, Dict, Any
from app.intelligence.coordinator.models import ClinicalContext
from app.intelligence.recommendations.engines import (
    EmergencyRecommendationEngine,
    MonitoringRecommendationEngine,
    MedicationSafetyRecommendationEngine,
    LifestyleRecommendationEngine,
    FollowupRecommendationEngine,
    PreventiveRecommendationEngine
)

class RecommendationCoordinator:
    def __init__(self):
        # Strict Execution Order
        self.engines = [
            EmergencyRecommendationEngine(),
            MonitoringRecommendationEngine(),
            MedicationSafetyRecommendationEngine(),
            LifestyleRecommendationEngine(),
            FollowupRecommendationEngine(),
            PreventiveRecommendationEngine()
        ]
        
    def generate_all(self, context: ClinicalContext) -> List[Dict[str, Any]]:
        all_recommendations = []
        for engine in self.engines:
            recs = engine.generate(context)
            all_recommendations.extend(recs)
        return all_recommendations

recommendation_coordinator = RecommendationCoordinator()
