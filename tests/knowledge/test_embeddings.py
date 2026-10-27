import pytest
from app.knowledge.embeddings.manager import EmbeddingModelManager
from app.knowledge.embeddings.provider import LocalSentenceTransformerProvider
from app.knowledge.embeddings.pipeline import EmbeddingPipeline
from app.knowledge.datasets.manifest import Chunk

def test_model_manager():
    manager = EmbeddingModelManager()
    manager.register_model("local-st", "1.0", 384, "local")
    assert manager.get_active_model().name == "local-st"
    assert manager.check_compatibility("local-st", "local-st")

def test_embedding_pipeline():
    manager = EmbeddingModelManager()
    manager.register_model("local-st", "1.0", 384, "local")
    provider = LocalSentenceTransformerProvider(dimension=384)
    pipeline = EmbeddingPipeline(provider, manager)
    
    chunk = Chunk(
        chunk_id="chk1",
        parent_record="rec1",
        title="Test",
        text="This is a test chunk.",
        token_count=5,
        category="general",
        priority=10,
        evidence_level="Unknown",
        dataset="test_ds",
        publisher="Test Pub",
        metadata={}
    )
    
    records = pipeline.process_chunks([chunk], "test_ds")
    assert len(records) == 1
    assert len(records[0].embedding_vector) == 384
