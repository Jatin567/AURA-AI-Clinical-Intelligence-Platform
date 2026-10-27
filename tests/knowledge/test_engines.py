import pytest
from app.knowledge.engines.chunking import ChunkEngine
from app.knowledge.engines.extractors import ExtractorFactory

def test_chunk_engine():
    engine = ChunkEngine(strategy="sentence")
    record = {"aura_id": "test1", "text": "This is sentence one. This is sentence two!"}
    chunks = engine.process_record(record)
    assert len(chunks) == 2
    assert chunks[0].text == "This is sentence one."

def test_extractors():
    extractor = ExtractorFactory.get_extractor("diseases")
    record = {"aura_id": "test1", "text": "Patient has a symptom of cough."}
    rels = extractor.extract_relationships(record)
    assert len(rels) > 0
    assert rels[0]["type"] == "has_symptom"
