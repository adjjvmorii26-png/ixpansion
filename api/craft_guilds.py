"""Wave 133 — Craft Guilds.

Guilds organize workers by craft domain. Each guild holds a monopoly
on its craft's tasks, maintains its own standards, and holds masters
who certify apprentices — creating distributed centers of expertise.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class Guild:
    """A skilled community organized around a craft."""

    def __init__(self, craft: str, standards: float = 0.5):
        self.craft = craft
        self.standards = max(0.0, min(1.0, standards))
        self.members: List[str] = []
        self.masters: List[str] = []
        self.completed_works = 0
        self.created = time.time()
        self.id = hashlib.sha256(f"guild:{craft}".encode()).hexdigest()[:10]

    def join(self, worker: str) -> None:
        if worker not in self.members:
            self.members.append(worker)

    def certify(self, worker: str) -> bool:
        if worker not in self.members:
            return False
        if worker not in self.masters:
            self.masters.append(worker)
        return True

    def complete_work(self, count: int = 1) -> None:
        self.completed_works += count

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "craft": self.craft, "standards": self.standards,
                "members": len(self.members), "masters": len(self.masters),
                "works": self.completed_works}


class CraftGuilds:
    """Manages the guild system of the workforce civilization."""

    def __init__(self):
        self._guilds: Dict[str, Guild] = {}
        self._certifications = 0

    def found(self, craft: str, standards: float = 0.5) -> Guild:
        if craft in self._guilds:
            return self._guilds[craft]
        guild = Guild(craft, standards)
        self._guilds[craft] = guild
        return guild

    def certify(self, craft: str, worker: str, reputation: float = 0.5) -> bool:
        guild = self._guilds.get(craft)
        if guild is None:
            return False
        if reputation < guild.standards:
            return False
        ok = guild.certify(worker)
        if ok:
            self._certifications += 1
        return ok

    def assign_work(self, craft: str, required_standards: float) -> Optional[Guild]:
        guild = self._guilds.get(craft)
        if guild is None or guild.standards < required_standards:
            return None
        guild.complete_work()
        return guild

    def status(self) -> Dict[str, Any]:
        return {"guilds": len(self._guilds), "certifications": self._certifications,
                "members": sum(len(g.members) for g in self._guilds.values()),
                "works": sum(g.completed_works for g in self._guilds.values())}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    guilds = CraftGuilds()
    return {"status": "active", "module": "craft_guilds",
            **guilds.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "protocol", "status": "active", "wave": "133", "module": "craft_guilds"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
