import pytest
from app.rag.retrieval_executor import RetrievalDecisionEngine

def test_retrieval_decision():
    engine = RetrievalDecisionEngine()
    
    assert engine.decide_strategy("chat", "Hello there") == "No Retrieval"
    assert engine.decide_strategy("chat", "According to guideline") == "Guideline Retrieval"
    assert engine.decide_strategy("chat", "Give me drug interactions") == "Drug Retrieval"
    assert engine.decide_strategy("chat", "I have chest pain") == "Hybrid Retrieval"
