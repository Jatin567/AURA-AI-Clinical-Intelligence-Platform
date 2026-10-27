from typing import Dict, Any, List
from app.orchestrator.tool_registry import ITool

class RetrievalDecisionEngine:
    def decide_strategy(self, intent: str, query: str) -> str:
        # Example naive routing
        lower_query = query.lower()
        if "hello" in lower_query or "hi" in lower_query:
            return "No Retrieval"
        if "guideline" in lower_query:
            return "Guideline Retrieval"
        if "drug" in lower_query:
            return "Drug Retrieval"
        return "Hybrid Retrieval"

class KnowledgeRetrievalTool(ITool):
    def __init__(self, hybrid_engine):
        self.hybrid_engine = hybrid_engine
        self.decision_engine = RetrievalDecisionEngine()

    def supports(self, intent: str) -> bool:
        return intent == "knowledge_search"

    def execute(self, params: Dict[str, Any]) -> Any:
        strategy = self.decision_engine.decide_strategy(params.get("intent", ""), params.get("query", ""))
        if strategy == "No Retrieval":
            return None
            
        return self.hybrid_engine.search({"query": params["query"], "strategy": strategy})

    def schema(self) -> Dict[str, Any]:
        return {"name": "knowledge_retrieval", "description": "Fetches medical evidence."}

    def metadata(self) -> Dict[str, Any]:
        return {"version": "1.0", "author": "AURA"}

class RetrievalExecutor:
    def __init__(self, retrieval_tool: KnowledgeRetrievalTool):
        self.tool = retrieval_tool

    def execute(self, intent: str, query: str):
        if self.tool.supports(intent):
            return self.tool.execute({"intent": intent, "query": query})
        return None
