from typing import Dict, Any
from app.knowledge.retrieval.interfaces import AgentTool

class RetrievalTool(AgentTool):
    def get_tool_schema(self) -> Dict[str, Any]:
        return {
            "name": "search_medical_evidence",
            "description": "Searches the AURA Knowledge Platform for medical evidence.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The medical query to search for."}
                },
                "required": ["query"]
            }
        }
