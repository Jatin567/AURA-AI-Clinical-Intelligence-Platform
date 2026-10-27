from typing import Dict

class PromptTemplateRegistry:
    def __init__(self):
        self.templates: Dict[str, str] = {
            "General Chat": "System: You are an AI. \nPatient: {patient}\nEvidence: {evidence}",
            "Drug Lookup": "System: Focus on Drug interactions. \nPatient: {patient}\nEvidence: {evidence}"
        }

    def get_template(self, intent: str) -> str:
        return self.templates.get(intent, self.templates["General Chat"])
