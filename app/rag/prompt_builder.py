from typing import Dict, Any

class PromptBuilder:
    def __init__(self, registry):
        self.registry = registry

    def build(self, context: Dict[str, Any]) -> str:
        # Determine intent (stub default to General Chat)
        intent = context.get("intent", "General Chat")
        template = self.registry.get_template(intent)
        
        # Stub prompt assembly
        patient_info = str(context.get("patient", ""))
        evidence_info = str(context.get("evidence", ""))
        
        prompt = template.replace("{patient}", patient_info).replace("{evidence}", evidence_info)
        return prompt
