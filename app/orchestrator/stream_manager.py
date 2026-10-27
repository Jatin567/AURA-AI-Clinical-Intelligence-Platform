from typing import Any, AsyncGenerator
import json
import asyncio

class StreamManager:
    """Manages SSE events: TEXT, CARD, STATUS, PROGRESS, TOKEN, TOOL, ERROR, COMPLETE, HEARTBEAT."""
    
    async def stream_events(self) -> AsyncGenerator[str, None]:
        # Stub implementation
        yield self._format_event("STATUS", "Starting session")
        await asyncio.sleep(0.1)
        yield self._format_event("HEARTBEAT", "alive")
        await asyncio.sleep(0.1)
        yield self._format_event("TEXT", "Hello from Orchestrator")
        yield self._format_event("COMPLETE", "Done")

    def _format_event(self, event_type: str, data: Any) -> str:
        payload = json.dumps({"type": event_type, "data": data})
        return f"data: {payload}\n\n"
