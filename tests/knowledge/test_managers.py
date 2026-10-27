import pytest
from app.knowledge.datasets.priority import DatasetPriorityManager
from app.knowledge.datasets.verify import DatasetVerifier

def test_priority_manager():
    pm = DatasetPriorityManager()
    assert pm.get_priority("WHO") == 100
    assert pm.get_priority("Unknown") == 10
    
def test_dataset_verifier():
    verifier = DatasetVerifier()
    class DummyManifest:
        publisher = "WHO"
        dataset_id = "1"
        checksum_sha256 = "dummy"
    errors = verifier.verify_manifest(DummyManifest())
    assert len(errors) == 0
