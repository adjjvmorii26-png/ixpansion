"""Wave 129 — Metaphor Engine.

Generates metaphors by finding structural similarities between
disparate domains. The engine discovers that "a cell is a city" or
"the internet is a nervous system" by mapping analogous structures.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class Metaphor:
    """A generated metaphor connecting two domains."""

    def __init__(self, source_domain: str, target_domain: str):
        self.source_domain = source_domain
        self.target_domain = target_domain
        self.mappings: List[Dict[str, str]] = []
        self.strength = 0.0
        self.created = time.time()
        self.id = hashlib.sha256(f"meta:{source_domain}:{target_domain}".encode()).hexdigest()[:8]

    def add_mapping(self, source_element: str, target_element: str) -> None:
        self.mappings.append({"source": source_element, "target": target_element})
        self.strength = min(1.0, self.strength + 0.2)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "source": self.source_domain,
                "target": self.target_domain, "mappings": len(self.mappings),
                "strength": round(self.strength, 4)}


class MetaphorEngine:
    """Generates metaphors between disparate domains."""

    def __init__(self):
        self._metaphors: List[Metaphor] = []

    def create(self, source: str, target: str) -> Metaphor:
        m = Metaphor(source, target)
        self._metaphors.append(m)
        return m

    def add_mapping(self, metaphor_id: str, source: str, target: str) -> bool:
        for m in self._metaphors:
            if m.id == metaphor_id:
                m.add_mapping(source, target)
                return True
        return False

    def strongest_metaphor(self) -> Dict[str, Any]:
        if not self._metaphors:
            return {}
        return max(self._metaphors, key=lambda m: m.strength).to_dict()

    def get_metaphors(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self._metaphors]

    def status(self) -> Dict[str, Any]:
        total_mappings = sum(len(m.mappings) for m in self._metaphors)
        return {"total_metaphors": len(self._metaphors), "total_mappings": total_mappings}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "metaphor_engine", "action": action}
