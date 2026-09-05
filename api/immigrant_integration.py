"""Wave 138 — Immigrant Integration.

Onboards workers and entities arriving from allied realms into the
civilization. Integration evaluates skill transferability, culture
fit, and residence status, then assigns mentors so newcomers reach
full participation quickly.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class Immigrant:
    """An arriving entity undergoing integration."""

    def __init__(self, name: str, origin: str, skills_transferable: float, culture_fit: float):
        self.name = name
        self.origin = origin
        self.skills_transferable = max(0.0, min(1.0, skills_transferable))
        self.culture_fit = max(0.0, min(1.0, culture_fit))
        self.status = "arriving"
        self.mentor: str = ""
        self.integration_score = 0.0
        self.created = time.time()
        self.id = hashlib.sha256(f"imm:{name}".encode()).hexdigest()[:10]

    def assign_mentor(self, mentor: str) -> None:
        self.mentor = mentor
        self.status = "integrating"

    def complete(self) -> float:
        self.integration_score = round((self.skills_transferable + self.culture_fit) / 2.0, 4)
        if self.integration_score >= 0.5:
            self.status = "integrated"
        return self.integration_score

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "origin": self.origin,
                "status": self.status, "mentor": self.mentor,
                "integration_score": self.integration_score}


class ImmigrantIntegration:
    """Manages the arrival and integration of newcomers."""

    def __init__(self):
        self._immigrants: Dict[str, Immigrant] = {}
        self._integrated = 0
        self._mentors_available: List[str] = []

    def register_mentor(self, name: str) -> None:
        self._mentors_available.append(name)

    def receive(self, name: str, origin: str, skills_transferable: float,
                culture_fit: float) -> Immigrant:
        immigrant = Immigrant(name, origin, skills_transferable, culture_fit)
        self._immigrants[immigrant.id] = immigrant
        if self._mentors_available:
            mentor = self._mentors_available.pop(0)
            immigrant.assign_mentor(mentor)
        return immigrant

    def integrate(self, immigrant_id: str) -> bool:
        immigrant = self._immigrants.get(immigrant_id)
        if immigrant is None or immigrant.status == "integrated":
            return False
        if immigrant.complete() >= 0.5:
            self._integrated += 1
            return True
        return False

    def status(self) -> Dict[str, Any]:
        return {"immigrants": len(self._immigrants),
                "integrated": self._integrated,
                "mentoring": sum(1 for i in self._immigrants.values()
                                 if i.status == "integrating")}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    integration = ImmigrantIntegration()
    return {"status": "active", "module": "immigrant_integration",
            **integration.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "sandbox", "status": "active", "wave": "138", "module": "immigrant_integration"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
