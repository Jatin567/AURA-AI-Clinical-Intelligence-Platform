import pytest
from app.knowledge.retrieval.ranking_engine import WeightedRankingEngine, RankingConfig
from app.knowledge.retrieval.models import SearchResult

def test_ranking_engine():
    config = RankingConfig(semantic_weight=0.5, keyword_weight=0.5)
    engine = WeightedRankingEngine(config)
    
    res1 = SearchResult(chunk_id="1", text="a", score=1.0, citation="c1", provenance_type="semantic")
    res2 = SearchResult(chunk_id="2", text="b", score=1.0, citation="c2", provenance_type="keyword")
    res3 = SearchResult(chunk_id="3", text="c", score=1.0, citation="c3", provenance_type="hybrid")
    
    ranked = engine.rank([res1, res2, res3])
    # hybrid should be ranked highest since it gets both semantic and keyword weight boosted
    assert ranked[0].chunk_id == "3"
