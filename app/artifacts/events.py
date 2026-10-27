from typing import Callable, List, Dict

class ArtifactEventBus:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, listener: Callable):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(listener)

    def publish(self, event_name: str, payload: dict):
        if event_name in self.listeners:
            for listener in self.listeners[event_name]:
                listener(payload)

artifact_events = ArtifactEventBus()
