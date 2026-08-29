"""Gossip Network — information spreads through agent social connections.

Like real gossip, information mutates as it passes between agents.
Each retelling adds flavor, removes details, and shifts emphasis.
The network tracks how rumors evolve and which agents are amplifiers
vs filters of information.
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


class Rumor:
    def __init__(self, origin: str, content: str):
        self.origin = origin
        self.original_content = content
        self.current_content = content
        self.hops: List[Dict[str, Any]] = []
        self.alive = True
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{content}:{self.timestamp}".encode()).hexdigest()[:8]

    def retell(self, reteller: str) -> Dict[str, Any]:
        words = self.current_content.split()
        mutations = [
            lambda w: w.upper() if random.random() > 0.7 else w,
            lambda w: f"~{w}~" if random.random() > 0.8 else w,
            lambda w: random.choice(["absolutely", "apparently", "supposedly"]) + " " + w,
        ]
        if words and random.random() > 0.4:
            idx = random.randint(0, len(words) - 1)
            words[idx] = random.choice(mutations)(words[idx])
        new_content = " ".join(words)
        distortion = 1.0 - len(set(new_content.split()) & set(self.original_content.split())) / max(len(self.original_content.split()), 1)
        self.current_content = new_content
        hop = {
            "reteller": reteller,
            "content": new_content[:80],
            "distortion": round(distortion, 3),
            "time": time.time(),
        }
        self.hops.append(hop)
        if distortion > 0.6 or len(self.hops) > 20:
            self.alive = False
        return hop

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "origin": self.origin,
            "current_content": self.current_content[:80],
            "hops": len(self.hops),
            "alive": self.alive,
            "distortion": round(
                1.0 - len(set(self.current_content.split()) & set(self.original_content.split())) /
                max(len(self.original_content.split()), 1), 3
            ),
        }


class GossipNetwork:
    def __init__(self):
        self.rumors: Dict[str, Rumor] = {}
        self.agent_reputation: Dict[str, float] = {}
        self.gossip_log: List[Dict[str, Any]] = []

    def start_rumor(self, agent: str, content: str) -> Dict[str, Any]:
        rumor = Rumor(agent, content)
        self.rumors[rumor.id] = rumor
        self.gossip_log.append({"event": "started", "agent": agent, "time": time.time()})
        return {"rumor": rumor.to_dict()}

    def retell_rumor(self, rumor_id: str, reteller: str) -> Dict[str, Any]:
        if rumor_id not in self.rumors:
            return {"error": "rumor not found"}
        rumor = self.rumors[rumor_id]
        if not rumor.alive:
            return {"error": "rumor has died"}
        hop = rumor.retell(reteller)
        self.agent_reputation.setdefault(reteller, 0.5)
        if hop["distortion"] < 0.1:
            self.agent_reputation[reteller] = min(1.0, self.agent_reputation[reteller] + 0.05)
        elif hop["distortion"] > 0.3:
            self.agent_reputation[reteller] = max(0.0, self.agent_reputation[reteller] - 0.03)
        self.gossip_log.append({"event": "retold", "reteller": reteller, "distortion": hop["distortion"], "time": time.time()})
        return {"hop": hop, "rumor": rumor.to_dict()}

    def alive_rumors(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self.rumors.values() if r.alive]

    def rumor_lifecycle(self, rumor_id: str) -> List[Dict[str, Any]]:
        if rumor_id not in self.rumors:
            return []
        return self.rumors[rumor_id].hops

    def agent_stats(self) -> Dict[str, Any]:
        return {k: round(v, 3) for k, v in sorted(self.agent_reputation.items(), key=lambda x: -x[1])}

    def network_stats(self) -> Dict[str, Any]:
        return {
            "total_rumors": len(self.rumors),
            "alive": sum(1 for r in self.rumors.values() if r.alive),
            "dead": sum(1 for r in self.rumors.values() if not r.alive),
            "total_hops": sum(len(r.hops) for r in self.rumors.values()),
            "total_agents": len(self.agent_reputation),
        }


_network = GossipNetwork()


def gossip_network_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "start":
        return _network.start_rumor(payload.get("agent", "whisperer"), payload.get("content", "something happened"))
    elif action == "retell":
        return _network.retell_rumor(payload.get("rumor_id", ""), payload.get("reteller", "gossiper"))
    elif action == "alive":
        return {"rumors": _network.alive_rumors()}
    elif action == "lifecycle":
        return {"hops": _network.rumor_lifecycle(payload.get("rumor_id", ""))}
    elif action == "agents":
        return {"agents": _network.agent_stats()}
    return {"status": "active", **_network.network_stats()}


handler = gossip_network_handler
