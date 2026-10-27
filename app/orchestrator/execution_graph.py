from typing import List, Callable, Dict
from app.orchestrator.ai_session import AISession

class ExecutionNode:
    def __init__(self, name: str, handler: Callable[[AISession], None]):
        self.name = name
        self.handler = handler

class ExecutionGraph:
    def __init__(self):
        self.nodes: List[ExecutionNode] = []

    def add_node(self, name: str, handler: Callable[[AISession], None]):
        self.nodes.append(ExecutionNode(name, handler))

    def execute(self, session: AISession):
        for node in self.nodes:
            try:
                # Add node start metric
                node.handler(session)
            except Exception as e:
                # Stub Error handling/Retry logic
                session.transition_state("ERROR")
                raise e
        session.transition_state("COMPLETED")
