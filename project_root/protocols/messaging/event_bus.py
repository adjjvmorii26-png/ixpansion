from collections import defaultdict
from typing import Any, Callable

from core.utils.logging import get_logger

logger = get_logger(__name__)


class EventBus:
    """Synchronous pub/sub event bus."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[dict[str, Any]], None]]] = defaultdict(list)

    def subscribe(self, topic: str, callback: Callable[[dict[str, Any]], None]) -> None:
        self._subscribers[topic].append(callback)

    def publish(self, topic: str, payload: dict[str, Any]) -> None:
        for cb in self._subscribers.get(topic, []):
            try:
                cb(payload)
            except Exception as exc:
                logger.error("subscriber error on '%s': %s", topic, exc)

    @property
    def topics(self) -> list[str]:
        return [t for t in self._subscribers if self._subscribers[t]]
