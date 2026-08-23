from collections import defaultdict
from typing import Any, Awaitable, Callable

Handler = Callable[[dict[str, Any]], Awaitable[None]]


class Reactor:
    """Central async event reactor with priority-ordered dispatch."""

    def __init__(self) -> None:
        self._channels: dict[str, list[tuple[int, Handler]]] = defaultdict(list)

    def on(self, event: str, handler: Handler, priority: int = 0) -> None:
        self._channels[event].append((priority, handler))
        self._channels[event].sort(key=lambda pair: pair[0], reverse=True)

    async def emit(self, event: str, payload: dict[str, Any]) -> list[Exception]:
        errors = []
        for _, handler in self._channels.get(event, []):
            try:
                await handler(payload)
            except Exception as exc:
                errors.append(exc)
        return errors

    @property
    def events(self) -> list[str]:
        return [e for e in self._channels if self._channels[e]]
