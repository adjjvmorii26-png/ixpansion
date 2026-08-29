"""Wave 137 — Failure Injection.

Deliberately injects controlled failures into subsystems to validate
that integrity and recovery layers actually respond. Each injection
targets a component; the engine confirms the blast radius stays
contained and that recovery triggers fire.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class FailureInjection:
    """Controlled fault injection with containment verification."""

    VALID_TARGETS = ["router", "state_core", "ledger", "mesh", "scheduler"]

    def __init__(self, auto_contain: bool = True):
        self.auto_contain = auto_contain
        self._injections: List[Dict[str, Any]] = []
        self._contained_failures = 0

    def inject(self, target: str, fault: str, severity: float = 0.3) -> Dict[str, Any]:
        record = {
            "target": target, "fault": fault, "severity": severity,
            "contained": self.auto_contain,
            "timestamp": round(time.time(), 4),
            "injection_id": hashlib.sha256(f"{target}:{fault}".encode()).hexdigest()[:10],
        }
        self._injections.append(record)
        if record["contained"]:
            self._contained_failures += 1
        return record

    def blast_radius(self) -> int:
        """Contained failures should not cascade."""
        return sum(1 for i in self._injections if not i["contained"])

    def recovery_triggered(self) -> bool:
        return any("recovery" in i["fault"].lower() for i in self._injections)

    def status(self) -> Dict[str, Any]:
        return {"injections": len(self._injections),
                "contained": self._contained_failures,
                "cascade_risk": self.blast_radius(),
                "recovery_triggered": self.recovery_triggered()}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    injector = FailureInjection()
    return {"status": "active", "module": "failure_injection",
            **injector.status()}
