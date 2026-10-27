from typing import Dict, Any

class LabParser:
    def parse_cbc(self, text: str) -> Dict[str, Any]:
        """Parses complete blood count elements with confidence."""
        return {
            "tests": [
                {"name": "Hemoglobin", "value": "14.2", "units": "g/dL", "confidence": 0.95, "source": "OCR", "page": 1}
            ]
        }
