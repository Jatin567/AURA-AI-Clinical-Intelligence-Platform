from abc import ABC, abstractmethod
from app.orchestrator.prompt_context import PromptContext

class PromptLayerBuilder(ABC):
    @abstractmethod
    def build(self, context: PromptContext) -> str:
        pass

class SystemPromptBuilder(PromptLayerBuilder):
    def build(self, context: PromptContext) -> str:
        return "System: You are an expert AI medical assistant."

class SafetyPromptBuilder(PromptLayerBuilder):
    def build(self, context: PromptContext) -> str:
        return "Safety: Do not diagnose. Only provide evidence-based info."

class PatientPromptBuilder(PromptLayerBuilder):
    def build(self, context: PromptContext) -> str:
        return f"Patient Profile: {context.patient_profile}"

class KnowledgePromptBuilder(PromptLayerBuilder):
    def build(self, context: PromptContext) -> str:
        if context.retrieved_evidence:
            return f"Evidence: {context.retrieved_evidence.compressed_context}"
        return ""

class MemoryPromptBuilder(PromptLayerBuilder):
    def build(self, context: PromptContext) -> str:
        return f"Memory: {context.memory}"

class ConversationPromptBuilder(PromptLayerBuilder):
    def build(self, context: PromptContext) -> str:
        return f"Current Question: {context.current_message}"

class FinalPromptAssembler:
    def __init__(self):
        self.layers = [
            SystemPromptBuilder(),
            SafetyPromptBuilder(),
            PatientPromptBuilder(),
            KnowledgePromptBuilder(),
            MemoryPromptBuilder(),
            ConversationPromptBuilder()
        ]

    def assemble(self, context: PromptContext) -> str:
        parts = []
        for layer in self.layers:
            content = layer.build(context)
            if content:
                parts.append(content)
        return "\n\n".join(parts)
