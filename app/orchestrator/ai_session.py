from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import time

class AISession(BaseModel):
    session_id: str
    user_id: str
    conversation_id: str
    state: str = "IDLE"
    provider: Optional[str] = None
    tools_selected: List[str] = Field(default_factory=list)
    retrieval_data: Dict[str, Any] = Field(default_factory=dict)
    memory_data: Dict[str, Any] = Field(default_factory=dict)
    context_data: Dict[str, Any] = Field(default_factory=dict)
    statistics: Dict[str, Any] = Field(default_factory=dict)
    start_time: float = Field(default_factory=time.time)

    def transition_state(self, new_state: str):
        self.state = new_state
