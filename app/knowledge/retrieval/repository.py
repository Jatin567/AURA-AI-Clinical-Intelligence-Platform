from typing import List, Dict
from app.knowledge.retrieval.models import EvidencePackage

class RetrievalRepository:
    def __init__(self):
        self._history: Dict[str, EvidencePackage] = {}

    def save_package(self, package: EvidencePackage) -> None:
        self._history[package.request_id] = package

    def get_package(self, request_id: str) -> EvidencePackage:
        return self._history.get(request_id)
