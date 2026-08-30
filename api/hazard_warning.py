"""Wave 137 — Hazard Warning.

An early-warning system that detects emerging hazards from
telemetry — rising load, integrity dips, resilience degradation —
and issues severity-ranked warnings so the civilization can
preempt shocks instead of reacting to them.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

SEVERITIES = ["info", "watch", "caution", "warning", "critical"]


class HazardWarning:
    """Early-warning system for emerging hazards."""

    def __init__(self):
        self._hazards: List[Dict[str, Any]] = []
        self._notified_actions = 0

    def evaluate(self, source: str, metric_name: str, value: float,
                 thresholds: Dict[str, float]) -> str:
        """thresholds: {'caution': x, 'critical': y}"""
        severity = "info"
        if value >= thresholds.get("critical", 1.0):
            severity = "critical"
        elif value >= thresholds.get("warning", 0.8):
            severity = "warning"
        elif value >= thresholds.get("caution", 0.6):
            severity = "caution"
        elif value >= thresholds.get("watch", 0.4):
            severity = "watch"
        hazard = {
            "source": source, "metric": metric_name, "value": round(value, 4),
            "severity": severity, "id": hashlib.sha256(f"{source}:{metric_name}".encode()).hexdigest()[:10],
            "timestamp": round(time.time(), 4),
        }
        if severity in ("warning", "critical"):
            self._notified_actions += 1
        self._hazards.append(hazard)
        return severity

    def active_hazards(self, min_severity: str = "caution") -> List[Dict[str, Any]]:
        idx = SEVERITIES.index(min_severity)
        return [h for h in self._hazards if SEVERITIES.index(h["severity"]) >= idx]

    def status(self) -> Dict[str, Any]:
        return {"hazards": len(self._hazards),
                "active": len(self.active_hazards()),
                "notified_actions": self._notified_actions}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    warning = HazardWarning()
    return {"status": "active", "module": "hazard_warning",
            **warning.status()}


def coherence_vitals() -> dict:
    """hazard_warning reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "hazard_warning_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['workforce_nexus', 'system_pulse', 'platform_pulse']

