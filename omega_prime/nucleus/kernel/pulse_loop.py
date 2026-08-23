import asyncio
import time
from typing import Any, Callable

from ..utilities.diagnostics import Diagnostics


class PulseLoop:
    """Time-sliced execution loop that yields control between pulses."""

    def __init__(self, pulse_hz: float = 10.0) -> None:
        self.pulse_interval = 1.0 / pulse_hz
        self._tasks: dict[str, Callable[[int], Any]] = {}
        self._running = False
        self._tick = 0
        self.diag = Diagnostics()

    def attach(self, name: str, fn: Callable[[int], Any]) -> None:
        self._tasks[name] = fn

    async def run(self, max_ticks: int | None = None) -> None:
        self._running = True
        while self._running:
            start = time.monotonic()
            for name, fn in self._tasks.items():
                t0 = time.monotonic()
                fn(self._tick)
                self.diag.record_timing(f"task.{name}", (time.monotonic() - t0) * 1000)
            elapsed = time.monotonic() - start
            sleep_for = max(0.0, self.pulse_interval - elapsed)
            await asyncio.sleep(sleep_for)
            self._tick += 1
            if max_ticks and self._tick >= max_ticks:
                self.stop()

    def stop(self) -> None:
        self._running = False

    @property
    def tick(self) -> int:
        return self._tick
