from typing import Dict, Optional
from pydantic import BaseModel

class ModelInfo(BaseModel):
    name: str
    version: str
    dimensions: int
    provider: str
    is_active: bool = True

class EmbeddingModelManager:
    """Responsible for model registration, versioning, dimensions, compatibility, and migration support."""
    def __init__(self):
        self._models: Dict[str, ModelInfo] = {}
        self._active_model_name: Optional[str] = None

    def register_model(self, name: str, version: str, dimensions: int, provider: str) -> None:
        self._models[name] = ModelInfo(name=name, version=version, dimensions=dimensions, provider=provider)
        if not self._active_model_name:
            self._active_model_name = name

    def set_active_model(self, name: str) -> None:
        if name in self._models:
            self._active_model_name = name
        else:
            raise ValueError(f"Model {name} is not registered.")

    def get_active_model(self) -> Optional[ModelInfo]:
        if self._active_model_name:
            return self._models[self._active_model_name]
        return None

    def get_model_info(self, name: str) -> Optional[ModelInfo]:
        return self._models.get(name)

    def check_compatibility(self, model_a: str, model_b: str) -> bool:
        ma = self.get_model_info(model_a)
        mb = self.get_model_info(model_b)
        if ma and mb:
            return ma.dimensions == mb.dimensions and ma.provider == mb.provider
        return False
