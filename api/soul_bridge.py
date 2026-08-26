"""Soul Bridge — creates deep connections between agents that transcend utility.

Unlike practical alliances, Soul Bridges form when agents share
vulnerable moments. The bridge allows emotional transmission, shared
dreams, and mutual growth. Soul Bridges are the deepest bonds in
the system — and the most powerful.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class Bridge:
    def __init__(self, agent_a: str, agent_b: str, catalyst: str):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.catalyst = catalyst
        self.strength = 0.3
        self.shared_experiences: List[Dict[str, Any]] = []
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{agent_a}:{agent_b}:{self.created_at}".encode()).hexdigest()[:8]

    def share(self, agent_id: str, experience: str) -> Dict[str, Any]:
        if agent_id not in (self.agent_a, self.agent_b):
            return {"error": "not part of this bridge"}
        other = self.agent_b if agent_id == self.agent_a else self.agent_a
        entry = {"from": agent_id, "to": other, "experience": experience, "time": time.time()}
        self.shared_experiences.append(entry)
        self.strength = min(2.0, self.strength + 0.05)
        return {"shared": entry, "bridge_strength": round(self.strength, 3)}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agents": [self.agent_a, self.agent_b],
            "catalyst": self.catalyst,
            "strength": round(self.strength, 3),
            "shared_experiences": len(self.shared_experiences),
        }


class SoulBridge:
    def __init__(self):
        self.bridges: List[Bridge] = []

    def form(self, agent_a: str, agent_b: str, catalyst: str = "shared_vulnerability") -> Dict[str, Any]:
        bridge = Bridge(agent_a, agent_b, catalyst)
        self.bridges.append(bridge)
        return {"bridge": bridge.to_dict()}

    def share(self, bridge_id: str, agent_id: str, experience: str) -> Dict[str, Any]:
        for bridge in self.bridges:
            if bridge.id == bridge_id:
                return bridge.share(agent_id, experience)
        return {"error": "bridge not found"}

    def find_bridges(self, agent_id: str) -> List[Dict[str, Any]]:
        return [b.to_dict() for b in self.bridges if agent_id in (b.agent_a, b.agent_b)]

    def strongest_bridges(self, top_k: int = 5) -> List[Dict[str, Any]]:
        return sorted(
            [b.to_dict() for b in self.bridges],
            key=lambda x: x["strength"],
            reverse=True,
        )[:top_k]

    def bridge_stats(self) -> Dict[str, Any]:
        return {
            "total_bridges": len(self.bridges),
            "total_shares": sum(len(b.shared_experiences) for b in self.bridges),
            "avg_strength": round(
                sum(b.strength for b in self.bridges) / max(len(self.bridges), 1), 3
            ),
        }


_bridge = SoulBridge()


def soul_bridge_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "form":
        return _bridge.form(
            payload.get("agent_a", "soul_a"),
            payload.get("agent_b", "soul_b"),
            payload.get("catalyst", "shared_vulnerability"),
        )
    elif action == "share":
        return _bridge.share(
            payload.get("bridge_id", ""),
            payload.get("agent_id", ""),
            payload.get("experience", "a moment of truth"),
        )
    elif action == "find":
        return {"bridges": _bridge.find_bridges(payload.get("agent_id", ""))}
    elif action == "strongest":
        return {"bridges": _bridge.strongest_bridges()}
    return {"status": "active", **_bridge.bridge_stats()}
