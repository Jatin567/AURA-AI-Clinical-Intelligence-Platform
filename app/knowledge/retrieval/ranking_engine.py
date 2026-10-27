from typing import List
from pydantic import BaseModel
from app.knowledge.retrieval.interfaces import RankingEngine
from app.knowledge.retrieval.models import SearchResult

class RankingConfig(BaseModel):
    semantic_weight: float = 0.40
    keyword_weight: float = 0.20
    dataset_priority_weight: float = 0.15
    evidence_level_weight: float = 0.10
    entity_match_weight: float = 0.10
    graph_weight: float = 0.05

class WeightedRankingEngine(RankingEngine):
    def __init__(self, config: RankingConfig = RankingConfig()):
        self.config = config

    def rank(self, results: List[SearchResult]) -> List[SearchResult]:
        for res in results:
            # Stub score recalculation based on provenance type
            if res.provenance_type == "semantic":
                res.score *= self.config.semantic_weight
            elif res.provenance_type == "keyword":
                res.score *= self.config.keyword_weight
            elif res.provenance_type == "hybrid":
                # Boost hybrid
                res.score *= (self.config.semantic_weight + self.config.keyword_weight)
                
        return sorted(results, key=lambda x: x.score, reverse=True)
