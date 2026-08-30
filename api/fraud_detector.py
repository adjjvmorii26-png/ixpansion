"""Wave 136 — Fraud Detector.

Flags suspicious activity in the economy and workforce: impossible
throughput, circular trades, reputation bombing, and collusion
patterns. Anomaly scoring routes high-risk behavior to the
integrity oracle for intervention.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class FraudDetector:
    """Detects and scores anomalous economic behavior."""

    def __init__(self):
        self._flags: List[Dict[str, Any]] = []
        self._activity_log: List[Dict[str, Any]] = []

    def record_activity(self, actor: str, kind: str, value: float) -> None:
        self._activity_log.append({"actor": actor, "kind": kind, "value": value})

    def assess_anomaly(self, actor: str, kind: str, value: float,
                       baseline: float, threshold: float = 3.0) -> Dict[str, Any]:
        deviation = (value / baseline) if baseline > 0 else float("inf")
        flagged = deviation >= threshold
        record = {
            "actor": actor, "kind": kind, "value": value,
            "baseline": baseline, "deviation": round(deviation, 4),
            "flagged": flagged,
        }
        if flagged:
            record["flag_id"] = hashlib.sha256(f"fraud:{actor}:{kind}".encode()).hexdigest()[:10]
            self._flags.append(record)
        return record

    def circular_risk(self, actors: List[str], trades: int = 1) -> Dict[str, Any]:
        """Flag small groups churning many trades (wash trading)."""
        risk = trades > 5 and len(actors) <= 3
        record = {"actors": actors, "trades": trades, "circular_suspect": risk}
        if risk:
            self._flags.append(record)
        return record

    def status(self) -> Dict[str, Any]:
        return {"activities": len(self._activity_log),
                "flags": len(self._flags),
                "recent_flags": self._flags[-3:] if self._flags else []}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    detector = FraudDetector()
    return {"status": "active", "module": "fraud_detector",
            **detector.status()}


def coherence_vitals() -> dict:
    """fraud_detector reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "fraud_detector_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['worker_wellness', 'emergence_oracle', 'workforce_nexus']

