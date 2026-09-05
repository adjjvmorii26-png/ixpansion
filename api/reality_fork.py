"""Wave 128 — Reality Fork.

Creates forks of reality — alternative system states that branch off
from the main timeline. Agents can explore forked realities, make
different choices, and merge insights back into the main line.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class RealityFork:
    """An alternative system state branching from the main timeline."""

    def __init__(self, name: str, parent_id: Optional[str] = None):
        self.name = name
        self.parent_id = parent_id
        self.created = time.time()
        self.events: List[str] = []
        self.merged = False
        self.entropy = 0.0
        self.id = hashlib.sha256(f"fork:{name}:{self.created}".encode()).hexdigest()[:10]

    def add_event(self, event: str) -> None:
        self.events.append(event)
        self.entropy += 0.05

    def merge(self) -> Dict[str, Any]:
        self.merged = True
        return {"fork": self.name, "events": len(self.events),
                "entropy": round(self.entropy, 4), "merged": True}

    def diverge(self, event: str) -> "RealityFork":
        child = RealityFork(f"{self.name}_branch", parent_id=self.id)
        child.add_event(event)
        return child

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "parent": self.parent_id,
                "events": len(self.events), "entropy": round(self.entropy, 4),
                "merged": self.merged}


class RealityForkManager:
    """Manages parallel reality forks."""

    def __init__(self):
        self._forks: Dict[str, RealityFork] = {}
        self._merge_count = 0

    def fork(self, name: str, parent_id: Optional[str] = None) -> RealityFork:
        fork = RealityFork(name, parent_id)
        self._forks[fork.id] = fork
        return fork

    def branch(self, fork_id: str, event: str) -> Optional[RealityFork]:
        fork = self._forks.get(fork_id)
        if not fork:
            return None
        child = fork.diverge(event)
        self._forks[child.id] = child
        return child

    def merge_fork(self, fork_id: str) -> Dict[str, Any]:
        fork = self._forks.get(fork_id)
        if not fork:
            return {"error": "fork not found"}
        result = fork.merge()
        self._merge_count += 1
        return result

    def unmerged_forks(self) -> List[Dict[str, Any]]:
        return [f.to_dict() for f in self._forks.values() if not f.merged]

    def status(self) -> Dict[str, Any]:
        return {"total_forks": len(self._forks), "merged": self._merge_count,
                "unmerged": len(self._forks) - self._merge_count}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "reality_fork", "action": action}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "128", "module": "reality_fork"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
