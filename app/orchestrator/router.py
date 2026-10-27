import re

class DeterministicRouter:
    """
    Lightweight, deterministic intent router.
    Avoids LLM latency by using keyword/regex heuristics to route messages.
    """
    
    KNOWLEDGE_KEYWORDS = [
        "guideline", "guidelines", "treatment for", "what is", "how do you treat",
        "side effects", "dosage", "medication for", "cure for", "research on",
        "evidence", "drug info"
    ]
    
    CLINICAL_KEYWORDS = [
        "pain", "headache", "feel", "hurt", "symptoms", "fever", "nausea", 
        "vomit", "dizzy", "weak", "numb", "bleed", "cough", 
        "chest", "breathe", "shortness of breath", "fatigue", "sick",
        "swollen", "rash", "my ", "i have ", "i've had ", "i am "
    ]
    
    def route(self, message: str) -> str:
        msg_lower = message.lower()
        
        # 1. Check for Knowledge Search
        for kw in self.KNOWLEDGE_KEYWORDS:
            if kw in msg_lower:
                # If they say "my treatment", it might be clinical, but we'll stick to a simple heuristic
                if "my " not in msg_lower and "i " not in msg_lower:
                    return "knowledge_search"
                if "guideline" in msg_lower:
                    return "knowledge_search"
                    
        # 2. Check for Clinical Intake
        for kw in self.CLINICAL_KEYWORDS:
            if kw in msg_lower:
                return "clinical_intake"
                
        # 3. Default to General Chat
        return "general_chat"

router = DeterministicRouter()
