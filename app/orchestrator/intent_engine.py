from typing import Tuple, Dict

class IntentEngine:
    def __init__(self):
        # We could use an LLM or fast classifier here
        pass
        
    async def classify(self, text: str) -> Tuple[str, float]:
        """Returns the primary intent and a confidence score."""
        return ("general_chat", 0.95)

intent_engine = IntentEngine()
