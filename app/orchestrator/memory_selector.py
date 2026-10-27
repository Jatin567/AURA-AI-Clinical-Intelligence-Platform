from typing import Dict, Any, List

class MemorySelector:
    """Selects Relevant Long Memory, Recent Memory, Patient Memory, and Summaries."""
    
    def select_memory(self, raw_memory: Dict[str, Any]) -> Dict[str, Any]:
        # Stub implementation
        return {
            "recent": raw_memory.get("recent_messages", [])[-5:], # last 5 messages
            "long_term": raw_memory.get("long_term_highlights", []),
            "patient_summary": raw_memory.get("patient_summary", ""),
            "conversation_summary": raw_memory.get("conversation_summary", "")
        }
