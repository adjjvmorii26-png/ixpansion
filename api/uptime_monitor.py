"""Wave 139 — Uptime Monitor.

Reports the platform's operational uptime: request success windows,
cumulative availability percentage, and the current degradation
state. Fires a synthetic "blip" whenever availability dips below
the committed target.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class UptimeMonitor:
    """Tracks platform availability and degradation events."""

    def __init__(self, target: float = 0.99):
        self.target = target
        self._windows: List[Dict[str, Any]] = []
        self._blips = 0

    def record_request(self, success: bool, now: float = 0.0) -> Dict[str, float]:
        now = now or time.time()
        window = {"time": round(now, 4), "success": success}
        self._windows.append(window)
        return window

    def availability(self) -> float:
        if not self._windows:
            return 1.0
        return round(sum(1 for w in self._windows if w["success"]) / len(self._windows), 4)

    def capacity_used(self) -> int:
        return len(self._windows)

    def status(self) -> Dict[str, Any]:
        avail = self.availability()
        degraded = avail < self.target
        if degraded:
            self._blips += 1
        return {"availability": avail, "target": self.target,
                "degraded": degraded, "requests": len(self._windows),
                "blips": self._blips}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    monitor = UptimeMonitor()
    return {"status": "active", "module": "uptime_monitor",
            **monitor.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "organ", "status": "active", "wave": "139", "module": "uptime_monitor"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
