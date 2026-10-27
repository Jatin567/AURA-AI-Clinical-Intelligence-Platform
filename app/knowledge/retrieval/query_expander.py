from typing import List
from app.knowledge.retrieval.interfaces import QueryExpansionEngine

class SynonymsQueryExpander(QueryExpansionEngine):
    def __init__(self):
        # Stub for SynonymManager
        self.synonyms = {"chest pain": ["angina", "cardiac chest pain"]}

    def expand(self, query: str) -> List[str]:
        expanded = [query]
        for term, syns in self.synonyms.items():
            if term in query.lower():
                expanded.extend(syns)
        return expanded
