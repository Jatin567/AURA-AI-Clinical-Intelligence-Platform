import json
import os
import logging
from typing import List, Optional
from app.interview.models import QuestionBankSchema, AdaptiveQuestion

logger = logging.getLogger("aura.interview.question_bank")


class QuestionBank:
    """
    Data-driven repository loader for adaptive clinical questions.
    Loads discriminative questions, targets, and option-to-evidence mappings.
    """

    DEFAULT_PATH = os.path.join(
        os.path.dirname(__file__), "data", "question_bank.json"
    )

    def __init__(self, json_path: Optional[str] = None):
        self.path = json_path or self.DEFAULT_PATH
        self._bank: Optional[QuestionBankSchema] = None
        self.load()

    def load(self) -> None:
        """Loads and validates the question bank JSON using Pydantic."""
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._bank = QuestionBankSchema.model_validate(data)
            logger.info(
                f"Successfully loaded {len(self._bank.questions)} questions "
                f"from question bank repository (v{self._bank.version})"
            )
        except Exception as e:
            logger.error(f"Failed to load question bank from {self.path}: {e}")
            raise RuntimeError(f"Question bank initialization error: {e}") from e

    def get_all_questions(self) -> List[AdaptiveQuestion]:
        """Returns all loaded questions."""
        if not self._bank:
            return []
        return self._bank.questions

    def get_question_by_id(self, question_id: str) -> Optional[AdaptiveQuestion]:
        """Finds a question by ID."""
        for q in self.get_all_questions():
            if q.question_id == question_id:
                return q
        return None

    def get_unasked_questions(self, asked_ids: List[str]) -> List[AdaptiveQuestion]:
        """Returns questions that have not yet been asked."""
        asked_set = set(asked_ids)
        return [q for q in self.get_all_questions() if q.question_id not in asked_set]
