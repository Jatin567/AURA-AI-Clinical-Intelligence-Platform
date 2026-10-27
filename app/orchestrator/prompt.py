from typing import List, Dict, Any
from abc import ABC, abstractmethod

class PromptBuilder(ABC):
    @abstractmethod
    def build(self, context: Any) -> str: pass

class SystemPromptBuilder(PromptBuilder):
    def build(self, context: Any) -> str:
        return "You are AURA, an elite medical AI Operating System."

class SafetyPromptBuilder(PromptBuilder):
    def build(self, context: Any) -> str:
        return "Always adhere to clinical safety guidelines. Do not diagnose."

class ContextPromptBuilder(PromptBuilder):
    def build(self, context: Any) -> str:
        return f"Patient Context: {context.patient}"

class KnowledgePromptBuilder(PromptBuilder):
    def build(self, context: Any) -> str:
        # We would pull compressed knowledge from the engine here
        return "Clinical Guidelines: [None]"

class ConversationPromptBuilder(PromptBuilder):
    def build(self, context: Any) -> str:
        return "Conversation History: []"

class FinalPromptAssembler:
    def __init__(self):
        self.builders = [
            SystemPromptBuilder(),
            SafetyPromptBuilder(),
            ContextPromptBuilder(),
            KnowledgePromptBuilder(),
            ConversationPromptBuilder()
        ]
        
    def assemble(self, context: Any, user_message: str) -> List[Dict[str, str]]:
        system_content = "\n\n".join([b.build(context) for b in self.builders])
        
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message}
        ]

prompt_assembler = FinalPromptAssembler()
