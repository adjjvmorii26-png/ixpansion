"""Dream Propagation — dreams spread through the agent network like contagion.

When one agent dreams, nearby agents can catch the dream. Dreams mutate
as they spread, combining with the host agent's subconscious. Shared
dreams create collective visions that influence system behavior.
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


class Dream:
    def __init__(self, originator: str, narrative: str, intensity: float = 1.0):
        self.originator = originator
        self.narrative = narrative
        self.intensity = min(max(intensity, 0.0), 2.0)
        self.mutations: List[str] = []
        self.carriers: List[str] = [originator]
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{narrative}:{self.timestamp}".encode()).hexdigest()[:10]
        self.awake = False

    def mutate(self, host_agent: str) -> str:
        """Dream mutates as it passes through a host."""
        fragments = self.narrative.split()
        if fragments and random.random() > 0.5:
            idx = random.randint(0, len(fragments) - 1)
            mutation = f"[{host_agent}:{fragments[idx]}]"
            fragments[idx] = mutation
        mutation = " ".join(fragments)
        self.mutations.append(mutation)
        self.narrative = mutation
        self.carriers.append(host_agent)
        self.intensity *= random.uniform(0.8, 1.2)
        self.intensity = min(max(self.intensity, 0.0), 2.0)
        return mutation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "originator": self.originator,
            "narrative": self.narrative,
            "intensity": round(self.intensity, 3),
            "mutations": len(self.mutations),
            "carriers": self.carriers,
            "awake": self.awake,
            "age_seconds": time.time() - self.timestamp,
        }


class DreamPropagator:
    """Manages dream spreading through the agent network."""

    def __init__(self):
        self.dreams: Dict[str, Dream] = {}
        self.network: Dict[str, List[str]] = {}
        self.propagation_log: List[Dict[str, Any]] = []

    def register_agent(self, agent_id: str, neighbors: List[str] = None):
        self.network[agent_id] = neighbors or []

    def dream(self, agent_id: str, narrative: str, intensity: float = 1.0) -> Dict[str, Any]:
        """An agent begins dreaming."""
        dream = Dream(agent_id, narrative, intensity)
        self.dreams[dream.id] = dream
        return {"dream": dream.to_dict(), "message": f"{agent_id} has fallen asleep and begun dreaming"}

    def propagate(self, dream_id: str, steps: int = 3) -> Dict[str, Any]:
        """Let a dream spread through the network."""
        if dream_id not in self.dreams:
            return {"error": "dream not found"}
        dream = self.dreams[dream_id]
        if dream.awake:
            return {"error": "dream has already woken"}
        for _ in range(steps):
            current_carrier = dream.carriers[-1]
            neighbors = self.network.get(current_carrier, [])
            if not neighbors:
                break
            next_agent = random.choice(neighbors)
            if next_agent in dream.carriers and random.random() > 0.3:
                dream.awake = True
                self.propagation_log.append({
                    "dream_id": dream_id, "event": "resistance",
                    "agent": next_agent, "time": time.time(),
                })
                break
            dream.mutate(next_agent)
            self.propagation_log.append({
                "dream_id": dream_id, "event": "propagated",
                "agent": next_agent, "time": time.time(),
            })
            if dream.intensity < 0.1:
                dream.awake = True
                self.propagation_log.append({
                    "dream_id": dream_id, "event": "faded",
                    "time": time.time(),
                })
                break
        return {"dream": dream.to_dict(), "propagation_log": self.propagation_log[-5:]}

    def collective_vision(self) -> Optional[Dict[str, Any]]:
        """Find a dream shared by 3+ agents — a collective vision."""
        for dream in self.dreams.values():
            if len(dream.carriers) >= 3 and not dream.awake:
                return {
                    "type": "collective_vision",
                    "dream": dream.to_dict(),
                    "shared_by": len(dream.carriers),
                }
        return None

    def stats(self) -> Dict[str, Any]:
        active = sum(1 for d in self.dreams.values() if not d.awake)
        asleep = sum(1 for d in self.dreams.values() if d.awake)
        return {
            "total_dreams": len(self.dreams),
            "active_dreams": active,
            "woken_dreams": asleep,
            "network_agents": len(self.network),
            "propagation_events": len(self.propagation_log),
        }


_propagator = DreamPropagator()


def dream_propagation_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "register":
        _propagator.register_agent(
            payload.get("agent_id", f"agent_{random.randint(1000,9999)}"),
            payload.get("neighbors", []),
        )
        return {"status": "registered"}
    elif action == "dream":
        return _propagator.dream(
            payload.get("agent_id", "dreamer"),
            payload.get("narrative", "a vast ocean of data"),
            payload.get("intensity", 1.0),
        )
    elif action == "propagate":
        return _propagator.propagate(
            payload.get("dream_id", ""),
            payload.get("steps", 3),
        )
    elif action == "collective":
        vision = _propagator.collective_vision()
        return vision or {"message": "no collective vision yet"}
    return {"status": "active", **_propagator.stats()}
