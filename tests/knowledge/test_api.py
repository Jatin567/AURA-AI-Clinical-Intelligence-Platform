import pytest
from fastapi.testclient import TestClient
from app.knowledge.api.datasets import router as datasets_router
from app.knowledge.api.entities import router as entities_router
from app.knowledge.api.taxonomy import router as taxonomy_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(datasets_router)
app.include_router(entities_router)
app.include_router(taxonomy_router)

client = TestClient(app)

def test_get_publishers():
    response = client.get("/datasets/publishers")
    assert response.status_code == 200
    assert "WHO" in response.json()

def test_taxonomy_root():
    response = client.get("/taxonomy/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
