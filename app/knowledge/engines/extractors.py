from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseExtractor(ABC):
    @abstractmethod
    def extract_relationships(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

class DiseaseExtractor(BaseExtractor):
    def extract_relationships(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        relationships = []
        text = record.get("text", "").lower()
        if "symptom" in text:
            relationships.append({"source": record["aura_id"], "target": "unknown_symptom", "type": "has_symptom"})
        if "treatment" in text:
            relationships.append({"source": record["aura_id"], "target": "unknown_treatment", "type": "treated_by"})
        return relationships

class DrugExtractor(BaseExtractor):
    def extract_relationships(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        relationships = []
        text = record.get("text", "").lower()
        if "contraindication" in text:
            relationships.append({"source": record["aura_id"], "target": "unknown_disease", "type": "contraindicated_for"})
        if "interaction" in text:
            relationships.append({"source": record["aura_id"], "target": "unknown_drug", "type": "interacts_with"})
        return relationships

class GuidelineExtractor(BaseExtractor):
    def extract_relationships(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        relationships = []
        # Stub implementation
        relationships.append({"source": record["aura_id"], "target": "unknown_disease", "type": "guideline_for"})
        return relationships

class LabExtractor(BaseExtractor):
    def extract_relationships(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        relationships = []
        text = record.get("text", "").lower()
        if "reference range" in text or "abnormal" in text:
            relationships.append({"source": record["aura_id"], "target": "unknown_disease", "type": "diagnostic_for"})
        return relationships

class ImagingExtractor(BaseExtractor):
    def extract_relationships(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        relationships = []
        text = record.get("text", "").lower()
        if "mri" in text or "ct" in text or "x-ray" in text:
            relationships.append({"source": record["aura_id"], "target": "unknown_disease", "type": "imaging_for"})
        return relationships

class ExtractorFactory:
    @staticmethod
    def get_extractor(category: str) -> BaseExtractor:
        if category == "diseases":
            return DiseaseExtractor()
        elif category == "drugs":
            return DrugExtractor()
        elif category == "guidelines":
            return GuidelineExtractor()
        elif category == "labs":
            return LabExtractor()
        elif category == "imaging":
            return ImagingExtractor()
        # Fallback or generic extractor
        return DiseaseExtractor()
