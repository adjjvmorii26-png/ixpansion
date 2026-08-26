"""Territory Map — agents claim, defend, and trade spatial regions.

The system is divided into territories that agents can claim, improve,
and defend. Territories generate resources based on their features.
Agents trade territories, form territorial alliances, and occasionally
wage territorial conflicts.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TERRAIN_FEATURES = ["forest", "mountain", "river", "plains", "desert", "coast", "cave", "ruins"]


class Territory:
    def __init__(self, name: str, x: int, y: int):
        self.name = name
        self.x = x
        self.y = y
        self.owner: Optional[str] = None
        self.features = random.sample(TERRAIN_FEATURES, k=random.randint(1, 3))
        self.resources = random.uniform(10, 100)
        self.defense = random.uniform(1, 10)
        self.improvements: List[str] = []
        self.created_at = time.time()

    def claim(self, agent_id: str) -> Dict[str, Any]:
        prev_owner = self.owner
        self.owner = agent_id
        return {"territory": self.name, "new_owner": agent_id, "previous_owner": prev_owner}

    def improve(self, improvement: str) -> Dict[str, Any]:
        self.improvements.append(improvement)
        self.resources *= 1.1
        return {"improvement": improvement, "resources": round(self.resources, 2)}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "position": [self.x, self.y],
            "owner": self.owner or "unclaimed",
            "features": self.features,
            "resources": round(self.resources, 2),
            "defense": round(self.defense, 2),
            "improvements": self.improvements,
        }


class TerritoryMap:
    def __init__(self, width: int = 5, height: int = 5):
        self.territories: Dict[str, Territory] = {}
        for x in range(width):
            for y in range(height):
                name = f"region_{x}_{y}"
                self.territories[name] = Territory(name, x, y)
        self.claim_log: List[Dict[str, Any]] = []

    def claim(self, territory_name: str, agent_id: str) -> Dict[str, Any]:
        if territory_name not in self.territories:
            return {"error": "territory not found"}
        result = self.territories[territory_name].claim(agent_id)
        self.claim_log.append({**result, "time": time.time()})
        return result

    def improve(self, territory_name: str, improvement: str) -> Dict[str, Any]:
        if territory_name not in self.territories:
            return {"error": "territory not found"}
        return self.territories[territory_name].improve(improvement)

    def agent_territories(self, agent_id: str) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self.territories.values() if t.owner == agent_id]

    def unclaimed(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self.territories.values() if not t.owner]

    def power_map(self) -> List[Dict[str, Any]]:
        owner_power: Dict[str, float] = {}
        for t in self.territories.values():
            if t.owner:
                owner_power[t.owner] = owner_power.get(t.owner, 0) + t.resources
        return sorted(
            [{"owner": k, "total_resources": round(v, 2)} for k, v in owner_power.items()],
            key=lambda x: x["total_resources"],
            reverse=True,
        )

    def map_stats(self) -> Dict[str, Any]:
        owners = set(t.owner for t in self.territories.values() if t.owner)
        return {
            "total_territories": len(self.territories),
            "claimed": sum(1 for t in self.territories.values() if t.owner),
            "unclaimed": sum(1 for t in self.territories.values() if not t.owner),
            "unique_owners": len(owners),
            "total_resources": round(sum(t.resources for t in self.territories.values()), 2),
        }


_map = TerritoryMap(5, 5)


def territory_map_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "claim":
        return _map.claim(payload.get("territory", "region_0_0"), payload.get("agent_id", "settler"))
    elif action == "improve":
        return _map.improve(payload.get("territory", "region_0_0"), payload.get("improvement", "farm"))
    elif action == "my_territories":
        return {"territories": _map.agent_territories(payload.get("agent_id", ""))}
    elif action == "unclaimed":
        return {"territories": _map.unclaimed()}
    elif action == "power":
        return {"power_map": _map.power_map()}
    return {"status": "active", **_map.map_stats()}
