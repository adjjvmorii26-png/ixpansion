"""Wave 133 — Heritage System.

Rituals and hard-won lessons are passed across worker generations.
Each worker carries a heritage chain from their mentors, enabling
knowledge transfer that outlives individual members.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class HeritageChain:
    """A chain of passed-down lessons and rituals."""

    def __init__(self, worker: str, ancestor: Optional[str] = None):
        self.worker = worker
        self.ancestor = ancestor
        self.lessons: List[str] = []
        self.created = time.time()
        self.id = hashlib.sha256(f"heritage:{worker}".encode()).hexdigest()[:10]

    def inherit(self, lessons: List[str]) -> None:
        for lesson in lessons:
            if lesson not in self.lessons:
                self.lessons.append(lesson)

    def depth(self) -> int:
        return len(self.lessons)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "worker": self.worker, "ancestor": self.ancestor,
                "lessons": self.lessons}


class HeritageSystem:
    """Tracks the inter-generational flow of workforce knowledge."""

    def __init__(self):
        self._chains: Dict[str, HeritageChain] = {}
        self._transfers = 0

    def initiate(self, worker: str, ancestor: Optional[str] = None) -> HeritageChain:
        chain = HeritageChain(worker, ancestor)
        self._chains[worker] = chain
        if ancestor and ancestor in self._chains:
            chain.inherit(self._chains[ancestor].lessons)
        return chain

    def teach(self, worker: str, lesson: str) -> bool:
        chain = self._chains.get(worker)
        if chain is None:
            return False
        chain.inherit([lesson])
        self._transfers += 1
        return True

    def lineage(self, worker: str) -> List[str]:
        chain = self._chains.get(worker)
        if chain is None:
            return []
        result = []
        cursor: Optional[str] = worker
        visited = set()
        while cursor and cursor not in visited and cursor in self._chains:
            visited.add(cursor)
            result.append(cursor)
            cursor = self._chains[cursor].ancestor
        return result

    def status(self) -> Dict[str, Any]:
        return {"workers": len(self._chains), "transfers": self._transfers,
                "total_lessons": sum(c.depth() for c in self._chains.values())}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    heritage = HeritageSystem()
    return {"status": "active", "module": "heritage_system",
            **heritage.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "protocol", "status": "active", "wave": "133", "module": "heritage_system"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
