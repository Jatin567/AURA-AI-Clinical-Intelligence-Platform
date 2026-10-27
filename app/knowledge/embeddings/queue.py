import queue
from typing import List, Any

class EmbeddingQueue:
    """Scalable batch processing queue for embedding generation."""
    def __init__(self, max_size: int = 10000):
        self._queue = queue.Queue(maxsize=max_size)

    def enqueue(self, item: Any) -> bool:
        try:
            self._queue.put_nowait(item)
            return True
        except queue.Full:
            return False

    def dequeue_batch(self, batch_size: int) -> List[Any]:
        batch = []
        try:
            for _ in range(batch_size):
                batch.append(self._queue.get_nowait())
        except queue.Empty:
            pass
        return batch

    def size(self) -> int:
        return self._queue.qsize()

    def is_empty(self) -> bool:
        return self._queue.empty()
