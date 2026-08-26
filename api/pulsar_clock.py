"""Wave 130 — Pulsar Clock.

A precision timekeeper based on pulsar signals — regular, predictable
beats that provide a reliable clock for the entire system, even when
local time becomes unreliable due to temporal distortions.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class PulsarBeat:
    """A single pulsar beat."""

    def __init__(self, pulsar_name: str, frequency: float):
        self.pulsar_name = pulsar_name
        self.frequency = frequency
        self.beat_count = 0
        self.last_beat = time.time()

    def tick(self) -> Dict[str, Any]:
        self.beat_count += 1
        self.last_beat = time.time()
        return {"pulsar": self.pulsar_name, "beat": self.beat_count,
                "frequency": self.frequency, "timestamp": self.last_beat}

    def to_dict(self) -> Dict[str, Any]:
        return {"pulsar": self.pulsar_name, "frequency": self.frequency,
                "beats": self.beat_count}


class PulsarClock:
    """Precision timekeeping based on pulsar signals."""

    def __init__(self):
        self._pulsars: List[PulsarBeat] = []
        self._total_ticks = 0

    def register_pulsar(self, name: str, frequency: float) -> PulsarBeat:
        pulsar = PulsarBeat(name, frequency)
        self._pulsars.append(pulsar)
        return pulsar

    def tick_all(self) -> List[Dict[str, Any]]:
        self._total_ticks += 1
        return [p.tick() for p in self._pulsars]

    def time_since(self, pulsar_name: str) -> float:
        for p in self._pulsars:
            if p.pulsar_name == pulsar_name:
                return time.time() - p.last_beat
        return -1.0

    def status(self) -> Dict[str, Any]:
        return {"total_pulsars": len(self._pulsars), "total_ticks": self._total_ticks}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "pulsar_clock", "action": action}
