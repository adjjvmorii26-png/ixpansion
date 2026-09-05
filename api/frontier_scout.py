"""Wave 138 — Frontier Scout.

Probes uncharted external ecosystems to assess expansion value. Each
expedition rates a target territory on opportunity, risk, and
compatibility; scouts mark the best candidate realms for the
federation to engage.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class Expedition:
    """A scouting expedition into an uncharted frontier."""

    def __init__(self, territory: str, opportunity: float, risk: float, compatibility: float):
        self.territory = territory
        self.opportunity = max(0.0, min(1.0, opportunity))
        self.risk = max(0.0, min(1.0, risk))
        self.compatibility = max(0.0, min(1.0, compatibility))
        self.rating = round((self.opportunity + self.compatibility) * (1.0 - self.risk), 4)
        self.created = time.time()
        self.id = hashlib.sha256(f"expedition:{territory}".encode()).hexdigest()[:10]

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "territory": self.territory,
                "opportunity": self.opportunity, "risk": self.risk,
                "compatibility": self.compatibility, "rating": self.rating}


class FrontierScout:
    """Ranks uncharted territories for expansion."""

    def __init__(self, engage_threshold: float = 0.5):
        self.engage_threshold = engage_threshold
        self._expeditions: Dict[str, Expedition] = {}
        self._engagements = 0

    def scout(self, territory: str, opportunity: float, risk: float,
              compatibility: float) -> Expedition:
        expedition = Expedition(territory, opportunity, risk, compatibility)
        self._expeditions[expedition.id] = expedition
        return expedition

    def prime_targets(self) -> List[Dict[str, Any]]:
        ranked = sorted(self._expeditions.values(), key=lambda e: e.rating, reverse=True)
        return [e.to_dict() for e in ranked if e.rating >= self.engage_threshold]

    def engage(self, expedition_id: str) -> bool:
        expedition = self._expeditions.get(expedition_id)
        if expedition is None or expedition.rating < self.engage_threshold:
            return False
        self._engagements += 1
        return True

    def status(self) -> Dict[str, Any]:
        return {"expeditions": len(self._expeditions),
                "prime_targets": len(self.prime_targets()),
                "engagements": self._engagements}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    scout = FrontierScout()
    return {"status": "active", "module": "frontier_scout",
            **scout.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "sandbox", "status": "active", "wave": "138", "module": "frontier_scout"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
