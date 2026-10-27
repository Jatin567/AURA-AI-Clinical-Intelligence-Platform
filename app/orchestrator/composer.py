import json
import uuid
from typing import Dict, Any, AsyncGenerator, List, Optional
from pydantic import BaseModel, Field

class UIAction(BaseModel):
    label: str
    action_type: str
    payload: Dict[str, Any]

class UIBlockSchema(BaseModel):
    """Standardized schema for all UI cards."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "1.0"
    type: str
    layout: str = "inline"
    priority: str = "normal"
    animation: str = "STREAM"
    theme: str = "default"
    permissions: List[str] = Field(default_factory=list)
    title: str = ""
    content: Any
    actions: List[UIAction] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

VALID_CARD_TYPES = {
    "ConditionCard", "RiskCard", "RecommendationCard", "EvidenceCard",
    "GuidelineCard", "DrugCard", "CalculatorCard", "EducationCard",
    "WarningCard", "TimelineCard", "FollowupCard", "CitationCard",
    "MissingInformationCard", "ExpandableReasoningCard"
}

class ResponseComposer:
    def format_sse_event(self, event_type: str, payload: Any) -> str:
        """Formats data into a valid Server-Sent Event."""
        if isinstance(payload, BaseModel):
            data_str = payload.model_dump_json()
        elif isinstance(payload, dict):
            data_str = json.dumps(payload)
        else:
            data_str = json.dumps({"text": str(payload)})
            
        return f"event: {event_type}\ndata: {data_str}\n\n"
        
    async def process_stream(self, llm_stream: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
        """Intercepts raw stream and wraps chunks in SSE events."""
        yield self.format_sse_event("STATUS", {"status": "generating"})
        
        async for chunk in llm_stream:
            yield self.format_sse_event("TEXT_CHUNK", chunk)
            
        yield self.format_sse_event("COMPLETE", {"status": "done"})

response_composer = ResponseComposer()
