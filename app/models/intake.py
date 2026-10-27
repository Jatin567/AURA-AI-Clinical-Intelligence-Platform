from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class IntakeQuestion(BaseModel):
    question_id: str
    text: str
    field_target: str  # dot-notation path into session, e.g. "patient_profile.age"
    input_type: Literal["text", "number", "yes_no", "multi_select"]
    options: Optional[List[str]] = None
    required: bool = True


class IntakeAnswer(BaseModel):
    question_id: str
    raw_answer: str
