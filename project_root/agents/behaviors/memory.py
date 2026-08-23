from collections import deque
from typing import Any


class MemoryBuffer:
    """Sliding-window episodic memory."""

    def __init__(self, capacity: int = 256) -> None:
        self._buffer: deque[dict[str, Any]] = deque(maxlen=capacity)

    def remember(self, entry: dict[str, Any]) -> None:
        self._buffer.append(entry)

    def recall(self, n: int = 10) -> list[dict[str, Any]]:
        return list(self._buffer)[-n:]

    def clear(self) -> None:
        self._buffer.clear()

    def __len__(self) -> int:
        return len(self._buffer)
