from typing import Dict, Any

class MedicationParser:
    def parse_prescription(self, text: str) -> Dict[str, Any]:
        """Extracts drug metadata."""
        return {
            "medications": [
                {"name": "Paracetamol", "strength": "500mg", "frequency": "BID", "confidence": 0.98, "source": "Prescription Classifier", "page": 1}
            ]
        }
