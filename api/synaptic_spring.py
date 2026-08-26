"""Wave 125 — Synaptic Spring.

Models synaptic plasticity — connections that strengthen with use and
weaken with disuse, creating a self-optimising network that naturally
routes traffic through the most efficient pathways.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Tuple


class Synapse:
    """A plastic synaptic connection."""

    def __init__(self, source: str, target: str, strength: float = 0.5):
        self.source = source
        self.target = target
        self.strength = strength
        self.use_count = 0
        self.last_used = time.time()
        self.created = time.time()

    def fire(self) -> float:
        self.use_count += 1
        self.strength = min(1.0, self.strength + 0.05)
        self.last_used = time.time()
        return self.strength

    def decay(self, amount: float = 0.01) -> float:
        self.strength = max(0.0, self.strength - amount)
        return self.strength

    def age_factor(self) -> float:
        hours_idle = (time.time() - self.last_used) / 3600
        return max(0.0, 1.0 - hours_idle * 0.01)

    def to_dict(self) -> Dict[str, Any]:
        return {"source": self.source, "target": self.target,
                "strength": round(self.strength, 4), "uses": self.use_count}


class SynapticSpring:
    """Self-optimising synaptic network."""

    def __init__(self, decay_rate: float = 0.01):
        self.decay_rate = decay_rate
        self._synapses: List[Synapse] = []
        self._connections: Dict[str, List[str]] = {}

    def connect(self, source: str, target: str, strength: float = 0.5) -> Synapse:
        syn = Synapse(source, target, strength)
        self._synapses.append(syn)
        self._connections.setdefault(source, []).append(target)
        return syn

    def stimulate(self, source: str) -> List[Dict[str, Any]]:
        results = []
        for syn in self._synapses:
            if syn.source == source:
                new_strength = syn.fire()
                results.append({"target": syn.target, "strength": round(new_strength, 4)})
        return results

    def global_decay(self) -> int:
        weakened = 0
        for syn in self._synapses:
            old = syn.strength
            syn.decay(self.decay_rate)
            if syn.strength < old:
                weakened += 1
        return weakened

    def strongest_pathways(self, top_n: int = 5) -> List[Dict[str, Any]]:
        sorted_syn = sorted(self._synapses, key=lambda s: s.strength, reverse=True)
        return [s.to_dict() for s in sorted_syn[:top_n]]

    def status(self) -> Dict[str, Any]:
        avg = sum(s.strength for s in self._synapses) / max(len(self._synapses), 1)
        return {"total_synapses": len(self._synapses), "avg_strength": round(avg, 4)}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "synaptic_spring", "action": action}
