"""Wave 138 — Federation Treaty.

Governs how the civilization forms alliances with other realms and
ecosystems. Each treaty defines shared resources, mutual defense
obligations, and dispute channels; treaties ratify only when both
parties satisfy the trust threshold.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class Treaty:
    """A ratified agreement between two realms."""

    def __init__(self, title: str, realm_a: str, realm_b: str,
                 shared_resources: List[str]):
        self.title = title
        self.realm_a = realm_a
        self.realm_b = realm_b
        self.shared_resources = shared_resources
        self.ratified = False
        self.mutual_defense = True
        self.created = time.time()
        self.id = hashlib.sha256(f"treaty:{title}".encode()).hexdigest()[:10]

    def ratify(self, trust_a: float, trust_b: float, threshold: float = 0.6) -> bool:
        if trust_a >= threshold and trust_b >= threshold:
            self.ratified = True
        return self.ratified

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "title": self.title, "realms": [self.realm_a, self.realm_b],
                "shared_resources": self.shared_resources, "ratified": self.ratified,
                "mutual_defense": self.mutual_defense}


class FederationTreaty:
    """Ratifies and tracks inter-realm alliance treaties."""

    def __init__(self):
        self._treaties: Dict[str, Treaty] = {}
        self._ratified_count = 0

    def propose(self, title: str, realm_a: str, realm_b: str,
                shared_resources: List[str]) -> Treaty:
        treaty = Treaty(title, realm_a, realm_b, shared_resources)
        self._treaties[treaty.id] = treaty
        return treaty

    def ratify(self, treaty_id: str, trust_a: float, trust_b: float) -> bool:
        treaty = self._treaties.get(treaty_id)
        if treaty is None:
            return False
        ok = treaty.ratify(trust_a, trust_b)
        if ok:
            self._ratified_count += 1
        return ok

    def active_treaties(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self._treaties.values() if t.ratified]

    def status(self) -> Dict[str, Any]:
        return {"treaties": len(self._treaties),
                "ratified": self._ratified_count,
                "active": len(self.active_treaties())}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    federation = FederationTreaty()
    return {"status": "active", "module": "federation_treaty",
            **federation.status()}
