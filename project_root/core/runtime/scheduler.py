import time
from typing import Any, Callable

from ..utils.logging import get_logger

logger = get_logger(__name__)


class Scheduler:
    """Simple tick-based scheduler for periodic tasks."""

    def __init__(self, tick_interval: float = 0.5) -> None:
        self.tick_interval = tick_interval
        self._tasks: dict[str, tuple[float, Callable[[], Any]]] = {}
        self._last_run: dict[str, float] = {}

    def register(self, name: str, interval: float, fn: Callable[[], Any]) -> None:
        self._tasks[name] = (interval, fn)
        self._last_run[name] = 0.0
        logger.debug("registered task '%s' every %.1fs", name, interval)

    def tick(self) -> dict[str, Any]:
        now = time.monotonic()
        results: dict[str, Any] = {}
        for name, (interval, fn) in self._tasks.items():
            if now - self._last_run[name] >= interval:
                try:
                    results[name] = fn()
                except Exception as exc:
                    logger.error("task '%s' failed: %s", name, exc)
                    results[name] = None
                self._last_run[name] = now
        return results
