import json
import os
import logging
from typing import List, Optional
from app.reasoning.models import ClinicalKnowledgeBase, ConditionDefinition

logger = logging.getLogger("aura.reasoning.repository")


class KnowledgeRepository:
    """
    Data-driven repository loader for clinical knowledge.
    Loads condition definitions, ICD-10 codes, references, and risk modifiers
    from a structured JSON file.
    """

    DEFAULT_PATH = os.path.join(
        os.path.dirname(__file__), "data", "clinical_knowledge.json"
    )

    def __init__(self, json_path: Optional[str] = None):
        self.path = json_path or self.DEFAULT_PATH
        self._knowledge_base: Optional[ClinicalKnowledgeBase] = None
        self.load()

    def load(self) -> None:
        """Loads and validates the JSON knowledge base using Pydantic."""
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._knowledge_base = ClinicalKnowledgeBase.model_validate(data)
            logger.info(
                f"Successfully loaded {len(self._knowledge_base.conditions)} conditions "
                f"from knowledge repository (v{self._knowledge_base.version})"
            )
        except Exception as e:
            logger.error(f"Failed to load clinical knowledge repository from {self.path}: {e}")
            raise RuntimeError(f"Clinical knowledge base initialization error: {e}") from e

    def get_all_conditions(self) -> List[ConditionDefinition]:
        """Returns all loaded condition definitions."""
        if not self._knowledge_base:
            return []
        return self._knowledge_base.conditions

    def get_condition_by_id(self, condition_id: str) -> Optional[ConditionDefinition]:
        """Finds a condition by its unique ID."""
        for cond in self.get_all_conditions():
            if cond.id == condition_id:
                return cond
        return None

    def get_version(self) -> str:
        """Returns repository version."""
        return self._knowledge_base.version if self._knowledge_base else "0.0.0"
