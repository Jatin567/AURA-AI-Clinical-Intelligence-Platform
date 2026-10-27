from typing import List
import numpy as np
from app.knowledge.vectorstore.interfaces import VectorStore

class VectorIndexer:
    """Handles incremental indexing and index versioning."""
    def __init__(self, store: VectorStore):
        self.store = store
        self.current_version = "1.0"

    def index_batch(self, embeddings: np.ndarray, ids: List[str]) -> None:
        self.store.batch_insert(embeddings, ids)

    def remove_batch(self, ids: List[str]) -> None:
        self.store.batch_delete(ids)

    def create_new_version(self) -> str:
        major, minor = self.current_version.split('.')
        self.current_version = f"{major}.{int(minor) + 1}"
        return self.current_version
