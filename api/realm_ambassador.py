"""Wave 138 — Realm Ambassador.

Diplomatic envoys representing the civilization in foreign realms.
Ambassadors build rapport, negotiate treaties, and report intelligence
back home. Their success depends on cultural alignment and the
trust they accrue abroad.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class Ambassador:
    """A diplomatic envoy stationed in a foreign realm."""

    def __init__(self, name: str, realm: str):
        self.name = name
        self.realm = realm
        self.rapport = 0.5
        self.missions = 0
        self.successes = 0
        self.posted = time.time()
        self.id = hashlib.sha256(f"amb:{name}:{realm}".encode()).hexdigest()[:10]

    def negotiate(self, difficulty: float) -> bool:
        """Returns whether the negotiation succeeded."""
        chance = self.rapport * (1.0 - difficulty)
        success = chance >= 0.4
        self.missions += 1
        if success:
            self.successes += 1
            self.rapport = min(1.0, self.rapport + 0.1)
        else:
            self.rapport = max(0.0, self.rapport - 0.05)
        return success

    def success_rate(self) -> float:
        return round(self.successes / self.missions, 4) if self.missions else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "realm": self.realm,
                "rapport": round(self.rapport, 4), "missions": self.missions,
                "success_rate": self.success_rate()}


class RealmAmbassador:
    """Deploys and tracks diplomatic envoys."""

    def __init__(self):
        self._ambassadors: Dict[str, Ambassador] = {}
        self._postings = 0

    def post(self, name: str, realm: str) -> Ambassador:
        ambassador = Ambassador(name, realm)
        self._ambassadors[ambassador.id] = ambassador
        self._postings += 1
        return ambassador

    def negotiate(self, ambassador_id: str, difficulty: float) -> bool:
        ambassador = self._ambassadors.get(ambassador_id)
        if ambassador is None:
            return False
        return ambassador.negotiate(difficulty)

    def best_diplomat(self) -> str:
        if not self._ambassadors:
            return "none"
        return max(self._ambassadors, key=lambda a: self._ambassadors[a].rapport)

    def status(self) -> Dict[str, Any]:
        return {"ambassadors": len(self._ambassadors), "postings": self._postings,
                "total_successes": sum(a.successes for a in self._ambassadors.values())}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    ambassador = RealmAmbassador()
    return {"status": "active", "module": "realm_ambassador",
            **ambassador.status()}
