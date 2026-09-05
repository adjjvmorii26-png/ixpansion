"""Wave 138 — Border Diplomacy.

Manages the soft borders between the civilization and foreign realms:
visa flows, resource-border taxes, and peaceful passage. Border
openness is tuned by trust; too open invites risk, too closed
starves the alliance.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class BorderDiplomacy:
    """Tunable border policy weighing openness against risk."""

    def __init__(self, openness: float = 0.5):
        self.openness = max(0.0, min(1.0, openness))
        self._crossings: List[Dict[str, Any]] = []
        self.border_tax_rate = 0.05

    def set_openness(self, value: float) -> None:
        self.openness = max(0.0, min(1.0, value))

    def passage(self, traveler: str, origin: str, destination: str,
                risk_level: float) -> bool:
        """Approve passage based on openness vs. traveler risk."""
        allowed = risk_level <= self.openness
        self._crossings.append({
            "traveler": traveler, "origin": origin, "destination": destination,
            "risk": risk_level, "allowed": allowed,
            "id": hashlib.sha256(f"cross:{traveler}".encode()).hexdigest()[:10],
        })
        return allowed

    def border_tariff(self, goods_value: float) -> float:
        return round(goods_value * self.border_tax_rate, 4)

    def risk_pressure(self) -> float:
        """Share of denied crossings (perceived threat)."""
        if not self._crossings:
            return 0.0
        denied = sum(1 for c in self._crossings if not c["allowed"])
        return round(denied / len(self._crossings), 4)

    def status(self) -> Dict[str, Any]:
        return {"openness": self.openness, "crossings": len(self._crossings),
                "risk_pressure": self.risk_pressure(),
                "border_tax_rate": self.border_tax_rate}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    border = BorderDiplomacy()
    return {"status": "active", "module": "border_diplomacy",
            **border.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "sandbox", "status": "active", "wave": "138", "module": "border_diplomacy"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
