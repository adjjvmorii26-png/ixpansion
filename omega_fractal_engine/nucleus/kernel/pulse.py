"""Heartbeat tick for all agents — the engine's circadian rhythm."""
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class PulseRecord:
    tick: int
    timestamp: float
    participants: list[str]
    mutations: int


class Pulse:
    def __init__(self, interval_s: float = 0.1) -> None:
        self.interval = interval_s
        self._tick = 0
        self._subscribers: dict[str, list[Callable[[int], Any]]] = defaultdict(list)
        self._last_fire: float = 0.0
        self.history: list[PulseRecord] = []
        self.max_history = 1000

    def subscribe(self, channel: str, fn: Callable[[int], Any]) -> None:
        self._subscribers[channel].append(fn)

    def fire(self) -> PulseRecord:
        now = time.monotonic()
        elapsed = now - self._last_fire
        self._tick += 1
        self._last_fire = now

        mutations = 0
        participants = []
        for channel, fns in self._subscribers.items():
            for fn in fns:
                result = fn(self._tick)
                if isinstance(result, dict) and result.get("mutated"):
                    mutations += 1
                    participants.append(channel)

        record = PulseRecord(tick=self._tick, timestamp=now,
                             participants=participants, mutations=mutations)
        self.history.append(record)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        return record

    @property
    def tick(self) -> int:
        return self._tick

    @property
    def bpm(self) -> float:
        if len(self.history) < 2:
            return 0.0
        span = self.history[-1].timestamp - self.history[0].timestamp
        if span <= 0:
            return 0.0
        return round(len(self.history) / span * 60, 1)
