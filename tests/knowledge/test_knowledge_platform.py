import pytest
from app.knowledge.datasets.priority import DatasetPriorityManager
from app.knowledge.engines.chunking import ChunkEngine
from app.knowledge.datasets.version import DatasetVersionManager

def test_priority_manager():
    manager = DatasetPriorityManager()
    assert manager.get_priority("WHO") == 100
    assert manager.get_priority("CDC") == 95
    assert manager.get_priority("Random") == 10
    assert manager.compare("WHO", "CDC") > 0
    assert manager.compare("Research Papers", "NIH") < 0

def test_conflict_resolution():
    manager = DatasetPriorityManager()
    facts = [
        {"fact": "A", "publisher": "Educational Sources"},
        {"fact": "B", "publisher": "WHO"},
        {"fact": "C", "publisher": "Clinical Trials"}
    ]
    resolved = manager.resolve_conflict(facts)
    assert resolved["publisher"] == "WHO"

def test_chunk_engine():
    engine = ChunkEngine(strategy="sentence")
    record = {
        "aura_id": "test_id",
        "title": "test",
        "text": "Sentence one. Sentence two! Sentence three?",
        "category": "misc"
    }
    chunks = engine.process_record(record)
    assert len(chunks) == 3
    assert chunks[0].text == "Sentence one."
    assert chunks[1].text == "Sentence two!"
    assert chunks[2].text == "Sentence three?"

def test_version_compatibility():
    manager = DatasetVersionManager()
    assert manager.check_compatibility("1.0.0", "1.1.0") == True
    assert manager.check_compatibility("1.0.0", "2.0.0") == False
