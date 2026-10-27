class EventBus:
    """Publishes specific lifecycle events allowing background processing."""
    
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type: str, handler):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def publish(self, event_type: str, payload: dict):
        # Stub synchronous publish
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                handler(payload)
