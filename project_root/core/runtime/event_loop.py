import asyncio
from collections import defaultdict
from typing import Any, Callable, Coroutine

from ..utils.logging import get_logger

logger = get_logger(__name__)

Handler = Callable[[dict[str, Any]], Coroutine[Any, Any, None]]


class EventLoop:
    """Async event loop with topic-based subscription."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        self._queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._running = False

    def subscribe(self, topic: str, handler: Handler) -> None:
        self._handlers[topic].append(handler)
        logger.debug("subscribed to '%s'", topic)

    async def publish(self, topic: str, payload: dict[str, Any]) -> None:
        await self._queue.put({"topic": topic, "payload": payload})

    async def start(self) -> None:
        self._running = True
        logger.info("event loop started")
        while self._running:
            try:
                msg = await asyncio.wait_for(self._queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                continue
            for handler in self._handlers.get(msg["topic"], []):
                try:
                    await handler(msg["payload"])
                except Exception as exc:
                    logger.error("handler error on '%s': %s", msg["topic"], exc)

    def stop(self) -> None:
        self._running = False
        logger.info("event loop stopped")
