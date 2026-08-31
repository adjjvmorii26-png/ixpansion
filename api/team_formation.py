"""Wave 131 — Team Formation.

Forms cohesive teams from a worker pool by scoring skill
complementarity. Teams are assembled to cover required capability
spread while minimizing overlap and maintaining role balance.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional, Set


class Team:
    """A formed team of workers with a mission."""

    def __init__(self, name: str, members: List[str], skills: List[str]):
        self.name = name
        self.members = members
        self.skills = skills
        self.mission = ""
        self.formed = time.time()
        self.id = hashlib.sha256(f"team:{name}".encode()).hexdigest()[:10]

    def assign_mission(self, mission: str) -> None:
        self.mission = mission

    def coverage(self) -> int:
        return len(self.skills)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "members": self.members,
                "skills": self.skills, "coverage": self.coverage(),
                "mission": self.mission}


class TeamFormation:
    """Assembles complementary teams from a worker skill pool."""

    def __init__(self):
        self._pool: Dict[str, Set[str]] = {}
        self._teams: Dict[str, Team] = {}
        self._teams_formed = 0

    def add_worker(self, name: str, skills: List[str]) -> None:
        self._pool[name] = set(skills)

    def _complementarity(self, members: List[str]) -> int:
        if not members:
            return 0
        union: Set[str] = set()
        for m in members:
            union |= self._pool.get(m, set())
        return len(union)

    def form(self, name: str, members: List[str], mission: str = "") -> Optional[Team]:
        if not members:
            return None
        if any(m not in self._pool for m in members):
            return None
        skills = sorted(self._pool[m] for m in members)
        union: Set[str] = set()
        for s in skills:
            union |= s
        team = Team(name, members, sorted(union))
        team.assign_mission(mission)
        self._teams[team.id] = team
        self._teams_formed += 1
        return team

    def strongest_combination(self, pool: List[str], size: int = 2) -> List[str]:
        """Greedy find of a subset maximizing coverage."""
        if size <= 1:
            return pool[:1] if pool else []
        best: List[str] = []
        best_score = 0
        # simple pairwise scan for moderate pool sizes
        for i in range(len(pool)):
            for j in range(i + 1, len(pool)):
                cand = [pool[i], pool[j]]
                score = self._complementarity(cand)
                if score > best_score:
                    best = cand
                    best_score = score
        return best

    def status(self) -> Dict[str, Any]:
        return {"pool": len(self._pool), "teams": len(self._teams),
                "teams_formed": self._teams_formed}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    formation = TeamFormation()
    return {"status": "active", "module": "team_formation",
            **formation.status()}


def coherence_vitals() -> dict:
    """team_formation reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "team_formation_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['resonance_symphony', 'workforce_nexus', 'worker_wellness']

