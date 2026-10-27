from abc import ABC, abstractmethod
from typing import Dict, Any, List

class SafetyInterceptor(ABC):
    @abstractmethod
    async def intercept_request(self, message: str, context: Any) -> bool:
        """Return False if unsafe."""
        pass
        
    @abstractmethod
    async def intercept_response(self, response: str, context: Any) -> bool:
        """Return False if unsafe."""
        pass

class ClinicalSafetyCheck(SafetyInterceptor):
    async def intercept_request(self, message: str, context: Any) -> bool:
        return True
        
    async def intercept_response(self, response: str, context: Any) -> bool:
        # Example check for diagnosing language
        if "I diagnose you with" in response:
            return False
        return True

class SafetyPipeline:
    def __init__(self):
        self.interceptors: List[SafetyInterceptor] = [
            ClinicalSafetyCheck()
        ]
        
    async def validate_request(self, message: str, context: Any) -> bool:
        for i in self.interceptors:
            if not await i.intercept_request(message, context):
                return False
        return True
        
    async def validate_response(self, response: str, context: Any) -> bool:
        for i in self.interceptors:
            if not await i.intercept_response(response, context):
                return False
        return True

safety_pipeline = SafetyPipeline()
