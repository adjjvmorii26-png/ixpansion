from __future__ import annotations
from collections import defaultdict
from collections.abc import Callable
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self.subscribers: defaultdict[str, list[Callable[[dict[str, Any]], None]]] = defaultdict(list)
        self.history: list[dict[str, Any]] = []

    def subscribe(self, topic: str, callback: Callable[[dict[str, Any]], None]) -> None:
        self.subscribers[topic].append(callback)

    def publish(self, topic: str, payload: dict[str, Any]) -> int:
        event = {"topic": topic, "payload": payload}
        self.history.append(event)
        for callback in self.subscribers[topic]:
            callback(payload)
        return len(self.subscribers[topic])

    def tail(self, count: int = 10) -> list[dict[str, Any]]:
        return self.history[-count:]
