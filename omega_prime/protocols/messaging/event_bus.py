from collections import defaultdict
from typing import Any, Callable

from ...nucleus.utilities.diagnostics import Diagnostics


class EventBus:
    """Synchronous topic-based pub/sub with diagnostics."""

    def __init__(self) -> None:
        self._subs: dict[str, list[Callable]] = defaultdict(list)
        self._diag = Diagnostics()

    def on(self, topic: str, fn: Callable) -> None:
        self._subs[topic].append(fn)

    def emit(self, topic: str, data: dict[str, Any]) -> None:
        self._diag.increment(f"emit.{topic}")
        for fn in self._subs.get(topic, []):
            try:
                fn(data)
            except Exception:
                self._diag.increment(f"error.{topic}")

    @property
    def topics(self) -> list[str]:
        return [t for t in self._subs if self._subs[t]]
