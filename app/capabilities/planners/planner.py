import yaml
from typing import Dict, Any

class WorkflowPlanner:
    def __init__(self, definitions_path: str = "app/capabilities/workflows/definitions/"):
        self.definitions_path = definitions_path

    def plan(self, intent: str) -> Dict[str, Any]:
        """Loads the YAML workflow corresponding to the intent."""
        # Stub logic mapping intent to yaml filename
        workflow_name = "medication_review" if "medication" in intent.lower() else "general_chat"
        file_path = f"{self.definitions_path}{workflow_name}.yaml"
        
        try:
            with open(file_path, "r") as f:
                workflow = yaml.safe_load(f)
            return workflow
        except FileNotFoundError:
            # Fallback
            return {"workflow": "fallback", "steps": []}
