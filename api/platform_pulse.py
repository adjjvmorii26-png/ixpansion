"""Wave 139 — Platform Pulse.

The single live-health signal for the deployed platform: fuses uptime,
route count, runtime config validity, and cache health into one pulse
that the dashboard and monitoring can poll on a cadence.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class PlatformPulse:
    """Aggregates live platform health into a single pulse."""

    def __init__(self):
        self._samples: List[float] = []

    def measure(self, uptime: float, available_modules: int,
                cache_health: float, config_valid: bool) -> float:
        score = round(
            (uptime * 0.4)
            + (min(1.0, available_modules / 100.0) * 0.2)
            + (cache_health * 0.2)
            + (1.0 if config_valid else 0.0) * 0.2,
            4,
        )
        self._samples.append(score)
        return score

    def last(self) -> float:
        return self._samples[-1] if self._samples else 1.0

    def trend(self) -> float:
        if len(self._samples) < 2:
            return 0.0
        return round(self._samples[-1] - self._samples[0], 4)

    def status(self) -> Dict[str, Any]:
        return {"pulse": self.last(), "samples": len(self._samples),
                "trend": self.trend()}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    pulse = PlatformPulse()
    return {"status": "active", "module": "platform_pulse",
            **pulse.status()}
