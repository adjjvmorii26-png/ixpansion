"""Wave 132 — Attention Reservoir.

Shared attention is a finite resource the workforce draws from.
Tasks compete for attention budget, and the reservoir routes focus
toward the highest-leverage work while preventing attention debt
from accumulating on any single worker.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class AttentionReservoir:
    """Manages the finite shared attention of the workforce."""

    def __init__(self, capacity: float = 100.0):
        self.capacity = capacity
        self._allocated: Dict[str, float] = {}
        self._debt: Dict[str, float] = {}

    def available(self) -> float:
        return max(0.0, self.capacity - sum(self._allocated.values()))

    def request(self, worker: str, amount: float) -> bool:
        if amount > self.available():
            return False
        self._allocated[worker] = self._allocated.get(worker, 0.0) + amount
        self._debt[worker] = max(0.0, self._debt.get(worker, 0.0) + amount * 0.1)
        return True

    def release(self, worker: str, amount: float) -> None:
        self._allocated[worker] = max(0.0, self._allocated.get(worker, 0.0) - amount)
        self._debt[worker] = max(0.0, self._debt.get(worker, 0.0) - amount * 0.15)

    def recharge(self, amount: float) -> bool:
        """Reduce accumulated attention debt."""
        self._debt = {w: max(0.0, d - amount) for w, d in self._debt.items()}
        return True

    def top_consumers(self, top: int = 3) -> List[str]:
        ranked = sorted(self._allocated, key=self._allocated.get, reverse=True)
        return ranked[:top]

    def status(self) -> Dict[str, Any]:
        return {"capacity": self.capacity, "allocated": round(sum(self._allocated.values()), 4),
                "available": round(self.available(), 4),
                "debt_total": round(sum(self._debt.values()), 4)}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    reservoir = AttentionReservoir()
    return {"status": "active", "module": "attention_reservoir",
            **reservoir.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "132", "module": "attention_reservoir"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
