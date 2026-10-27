from typing import List
from app.knowledge.retrieval.interfaces import EntityLinker

class RegistryEntityLinker(EntityLinker):
    def __init__(self):
        pass # Stub EntityRegistry

    def link(self, text: str) -> List[str]:
        # Stub
        if "chest pain" in text.lower():
            return ["AURA_ENT_001"]
        return []
