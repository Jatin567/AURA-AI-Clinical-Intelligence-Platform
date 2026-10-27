from typing import List, Dict, Any
from app.timeline.models import TimelineEntry, SeverityLevel

class SymptomTrendAnalyzer:
    @staticmethod
    def analyze(history: List[TimelineEntry]) -> Dict[str, Any]:
        result = {
            "recurring_symptoms": [],
            "newly_introduced_symptoms": [],
            "resolved_symptoms": [],
            "worsening_symptoms": [],
            "improving_symptoms": []
        }
        if len(history) < 2:
            return result
        
        # Analyze last two entries for simplicity, or across all history
        # For a full timeline, "newly introduced" means present in latest but not in previous.
        latest = set(history[-1].symptoms)
        previous = set(history[-2].symptoms) if len(history) >= 2 else set()
        all_previous = set()
        for entry in history[:-1]:
            all_previous.update(entry.symptoms)

        result["newly_introduced_symptoms"] = list(latest - all_previous)
        result["resolved_symptoms"] = list(previous - latest)
        
        # Recurring symptoms: present in multiple assessments
        symptom_counts = {}
        for entry in history:
            for sym in entry.symptoms:
                symptom_counts[sym] = symptom_counts.get(sym, 0) + 1
        
        result["recurring_symptoms"] = [sym for sym, count in symptom_counts.items() if count > 1]
        
        return result

class SeverityTrendAnalyzer:
    @staticmethod
    def analyze(history: List[TimelineEntry]) -> Dict[str, Any]:
        result = {
            "severity_escalation": False,
            "severity_de_escalation": False,
            "severity_trend_description": ""
        }
        if len(history) < 2:
            return result

        first_severity = SeverityLevel.from_string(history[0].severity)
        latest_severity = SeverityLevel.from_string(history[-1].severity)

        if latest_severity > first_severity:
            result["severity_escalation"] = True
            result["severity_trend_description"] = f"Severity escalated from {history[0].severity} to {history[-1].severity}."
        elif latest_severity < first_severity:
            result["severity_de_escalation"] = True
            result["severity_trend_description"] = f"Severity improved from {history[0].severity} to {history[-1].severity}."
        else:
            result["severity_trend_description"] = f"Severity remains stable at {history[-1].severity}."
            
        return result

class ConditionTrendAnalyzer:
    @staticmethod
    def analyze(history: List[TimelineEntry]) -> Dict[str, Any]:
        result = {
            "recurring_conditions": []
        }
        condition_counts = {}
        for entry in history:
            for cond in entry.possible_conditions:
                condition_counts[cond] = condition_counts.get(cond, 0) + 1
        
        result["recurring_conditions"] = [cond for cond, count in condition_counts.items() if count > 1]
        return result

class ConfidenceTrendAnalyzer:
    @staticmethod
    def analyze(history: List[TimelineEntry]) -> Dict[str, Any]:
        result = {
            "confidence_increases": {},
            "confidence_decreases": {}
        }
        if len(history) < 2:
            return result
        
        # Compare confidence of top_condition if it's the same across consecutive assessments
        prev = history[-2]
        curr = history[-1]
        
        if prev.top_condition and curr.top_condition and prev.top_condition == curr.top_condition:
            if prev.top_confidence is not None and curr.top_confidence is not None:
                diff = curr.top_confidence - prev.top_confidence
                if diff > 0:
                    result["confidence_increases"][curr.top_condition] = diff
                elif diff < 0:
                    result["confidence_decreases"][curr.top_condition] = abs(diff)
                    
        return result
