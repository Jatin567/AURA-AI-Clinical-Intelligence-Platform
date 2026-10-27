import pytest
from app.knowledge.core.interfaces import IDatasetRegistry, IHealthManager

# Just a simple stub test to verify interface importability and structure
def test_interfaces_exist():
    assert issubclass(IDatasetRegistry, object)
    assert issubclass(IHealthManager, object)
