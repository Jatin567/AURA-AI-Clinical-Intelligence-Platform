from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class AnswerRequest(BaseModel):
    answer: str
    question_id: Optional[str] = None

class SessionCreatedResponse(BaseModel):
    session_id: str
    expires_at: datetime

class QuestionResponse(BaseModel):
    question_id: str
    text: str
    input_type: str
    options: Optional[List[str]] = None
    intake_complete: bool = False

class AnswerResponse(BaseModel):
    answered: bool
    intake_complete: bool
