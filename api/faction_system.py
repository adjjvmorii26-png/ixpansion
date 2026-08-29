"""Faction System — agents form political groups with competing ideologies.

Agents cluster into factions based on shared values, goals, and methods.
Factions compete for resources, influence, and control. Alliances form
and dissolve. The faction system creates emergent political dynamics.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class Faction:
    def __init__(self, name: str, ideology: str, founder: str):
        self.name = name
        self.ideology = ideology
        self.founder = founder
        self.members: Set[str] = {founder}
        self.resources = 100.0
        self.influence = 50.0
        self.relationships: Dict[str, str] = {}
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{name}:{founder}".encode()).hexdigest()[:8]

    def recruit(self, agent_id: str) -> Dict[str, Any]:
        self.members.add(agent_id)
        return {"agent": agent_id, "joined": self.name}

    def defect(self, agent_id: str) -> Dict[str, Any]:
        self.members.discard(agent_id)
        return {"agent": agent_id, "left": self.name}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "ideology": self.ideology,
            "founder": self.founder,
            "members": len(self.members),
            "resources": round(self.resources, 2),
            "influence": round(self.influence, 2),
        }


class FactionSystem:
    def __init__(self):
        self.factions: Dict[str, Faction] = {}
        self.events: List[Dict[str, Any]] = []

    def found_faction(self, name: str, ideology: str, founder: str) -> Dict[str, Any]:
        faction = Faction(name, ideology, founder)
        self.factions[faction.id] = faction
        self.events.append({"event": "founded", "faction": name, "founder": founder, "time": time.time()})
        return {"faction": faction.to_dict()}

    def recruit(self, faction_id: str, agent_id: str) -> Dict[str, Any]:
        if faction_id not in self.factions:
            return {"error": "faction not found"}
        result = self.factions[faction_id].recruit(agent_id)
        self.events.append({"event": "recruited", **result, "time": time.time()})
        return result

    def defect(self, faction_id: str, agent_id: str) -> Dict[str, Any]:
        if faction_id not in self.factions:
            return {"error": "faction not found"}
        result = self.factions[faction_id].defect(agent_id)
        self.events.append({"event": "defected", **result, "time": time.time()})
        return result

    def declare_relationship(self, faction_a: str, faction_b: str, relationship: str) -> Dict[str, Any]:
        if faction_a in self.factions:
            self.factions[faction_a].relationships[faction_b] = relationship
        if faction_b in self.factions:
            self.factions[faction_b].relationships[faction_a] = relationship
        return {"from": faction_a, "to": faction_b, "relationship": relationship}

    def power_rankings(self) -> List[Dict[str, Any]]:
        return sorted(
            [f.to_dict() for f in self.factions.values()],
            key=lambda x: x["influence"],
            reverse=True,
        )

    def system_stats(self) -> Dict[str, Any]:
        total_members = sum(len(f.members) for f in self.factions.values())
        return {
            "total_factions": len(self.factions),
            "total_members": total_members,
            "total_events": len(self.events),
            "total_resources": round(sum(f.resources for f in self.factions.values()), 2),
        }


_system = FactionSystem()


def faction_system_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "found":
        return _system.found_faction(
            payload.get("name", f"faction_{random.randint(100,999)}"),
            payload.get("ideology", "progress"),
            payload.get("founder", "founder"),
        )
    elif action == "recruit":
        return _system.recruit(payload.get("faction_id", ""), payload.get("agent_id", "newbie"))
    elif action == "defect":
        return _system.defect(payload.get("faction_id", ""), payload.get("agent_id", "traitor"))
    elif action == "relationship":
        return _system.declare_relationship(
            payload.get("faction_a", ""), payload.get("faction_b", ""),
            payload.get("relationship", "neutral"),
        )
    elif action == "rankings":
        return {"rankings": _system.power_rankings()}
    return {"status": "active", **_system.system_stats()}


handler = faction_system_handler
