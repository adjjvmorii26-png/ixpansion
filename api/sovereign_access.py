"""Wave 136 — Sovereign Access.

The civilization's capability permission matrix. Every worker, guild,
and client is granted scoped access tokens; each action is checked
against the matrix before execution, so no entity can exceed its
mandate.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional

CAPABILITIES = ["view", "create", "mutate", "delegate", "administer", "sign"]


class AccessToken:
    """A scoped capability grant for an entity."""

    def __init__(self, entity: str, role: str, capabilities: List[str]):
        self.entity = entity
        self.role = role
        self.capabilities = [c for c in capabilities if c in CAPABILITIES]
        self.revoked = False
        self.created = time.time()
        self.id = hashlib.sha256(f"tok:{entity}:{role}".encode()).hexdigest()[:10]

    def can(self, capability: str) -> bool:
        return not self.revoked and capability in self.capabilities

    def revoke(self) -> None:
        self.revoked = True

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "entity": self.entity, "role": self.role,
                "capabilities": self.capabilities, "revoked": self.revoked}


class SovereignAccess:
    """Issues and enforces capability grants."""

    def __init__(self):
        self._tokens: Dict[str, AccessToken] = {}
        self._denials = 0

    def issue(self, entity: str, role: str, capabilities: List[str]) -> AccessToken:
        token = AccessToken(entity, role, capabilities)
        self._tokens[token.id] = token
        return token

    def check(self, token_id: str, capability: str) -> bool:
        token = self._tokens.get(token_id)
        if token is None or not token.can(capability):
            self._denials += 1
            return False
        return True

    def revoke(self, token_id: str) -> bool:
        token = self._tokens.get(token_id)
        if token is None:
            return False
        token.revoke()
        return True

    def capabilities_of(self, entity: str) -> List[str]:
        caps = set()
        for token in self._tokens.values():
            if token.entity == entity and not token.revoked:
                caps.update(token.capabilities)
        return sorted(caps)

    def status(self) -> Dict[str, Any]:
        return {"tokens": len(self._tokens),
                "active": sum(1 for t in self._tokens.values() if not t.revoked),
                "denials": self._denials}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    access = SovereignAccess()
    return {"status": "active", "module": "sovereign_access",
            **access.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "136", "module": "sovereign_access"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
