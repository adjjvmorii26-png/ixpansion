from collections import OrderedDict
from typing import Any


class MemoryCells:
    """LRU memory with episodic and semantic partitions."""

    def __init__(self, capacity: int = 512) -> None:
        self.capacity = capacity
        self._episodic: OrderedDict[str, Any] = OrderedDict()
        self._semantic: dict[str, Any] = {}

    def encode_episodic(self, key: str, value: Any) -> None:
        self._episodic[key] = value
        while len(self._episodic) > self.capacity:
            self._episodic.popitem(last=False)

    def consolidate(self, key: str, value: Any) -> None:
        self._semantic[key] = value

    def recall(self, key: str) -> Any | None:
        if key in self._episodic:
            self._episodic.move_to_end(key)
            return self._episodic[key]
        return self._semantic.get(key)

    @property
    def size(self) -> tuple[int, int]:
        return len(self._episodic), len(self._semantic)
