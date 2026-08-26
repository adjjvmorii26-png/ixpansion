"""Wave 120 — Cosmic Inventory.

Catalogs all emergent phenomena across the system as cosmic artifacts —
assigning each a classification, rarity, resonance signature, and
evolution potential. Creates a searchable atlas of emergent behaviour.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class CosmicArtifact:
    """A classified emergent phenomenon."""

    RARITY_LEVELS = ["common", "uncommon", "rare", "epic", "legendary", "mythic"]

    def __init__(self, name: str, domain: str, description: str = ""):
        self.name = name
        self.domain = domain
        self.description = description
        self.created = time.time()
        self.resonance = 0.5
        self.evolution_potential = 0.5
        self.rarity = "common"
        self.observations = 0
        self.id = hashlib.sha256(f"{name}:{domain}".encode()).hexdigest()[:12]

    def observe(self) -> None:
        self.observations += 1
        if self.observations > 5 and self.rarity != "mythic":
            idx = min(self.RARITY_LEVELS.index(self.rarity) + 1, len(self.RARITY_LEVELS) - 1)
            self.rarity = self.RARITY_LEVELS[idx]
        self.resonance = min(1.0, self.resonance + 0.02)
        self.evolution_potential = min(1.0, self.evolution_potential + 0.01)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "description": self.description,
            "rarity": self.rarity,
            "resonance": round(self.resonance, 4),
            "evolution_potential": round(self.evolution_potential, 4),
            "observations": self.observations,
            "created": self.created,
        }


class CosmicInventory:
    """Catalog and track all emergent phenomena as cosmic artifacts."""

    def __init__(self):
        self._artifacts: Dict[str, CosmicArtifact] = {}
        self._catalog_log: List[str] = []

    def catalog(self, name: str, domain: str, description: str = "") -> CosmicArtifact:
        artifact = CosmicArtifact(name, domain, description)
        self._artifacts[artifact.id] = artifact
        self._catalog_log.append(f"Cataloged {name} in {domain}")
        return artifact

    def observe_artifact(self, artifact_id: str) -> bool:
        artifact = self._artifacts.get(artifact_id)
        if not artifact:
            return False
        artifact.observe()
        return True

    def search_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        return [a.to_dict() for a in self._artifacts.values() if a.domain == domain]

    def search_by_rarity(self, rarity: str) -> List[Dict[str, Any]]:
        return [a.to_dict() for a in self._artifacts.values() if a.rarity == rarity]

    def get_artifacts(self) -> List[Dict[str, Any]]:
        return [a.to_dict() for a in self._artifacts.values()]

    def rarity_distribution(self) -> Dict[str, int]:
        dist: Dict[str, int] = {}
        for a in self._artifacts.values():
            dist[a.rarity] = dist.get(a.rarity, 0) + 1
        return dist

    def status(self) -> Dict[str, Any]:
        return {
            "total_artifacts": len(self._artifacts),
            "total_observations": sum(a.observations for a in self._artifacts.values()),
            "rarity_distribution": self.rarity_distribution(),
            "avg_resonance": (
                sum(a.resonance for a in self._artifacts.values()) / len(self._artifacts)
                if self._artifacts else 0.0
            ),
        }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "cosmic_inventory", "action": action}
