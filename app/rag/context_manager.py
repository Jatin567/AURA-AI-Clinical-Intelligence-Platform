from typing import Dict, Any

class ContextProvider:
    def provide(self, session: Any, evidence: Any) -> Dict[str, Any]:
        return {}

class PatientContextProvider(ContextProvider):
    def provide(self, session, evidence) -> Dict[str, Any]:
        return {"patient": session.context_data.get("patient_profile", {})}

class EvidenceContextProvider(ContextProvider):
    def provide(self, session, evidence) -> Dict[str, Any]:
        return {"evidence": evidence}

class RAGContextManager:
    def __init__(self):
        self.providers = [
            PatientContextProvider(),
            EvidenceContextProvider()
        ]

    def build_context(self, session: Any, evidence: Any) -> Dict[str, Any]:
        aggregated_context = {}
        for provider in self.providers:
            aggregated_context.update(provider.provide(session, evidence))
        return aggregated_context
