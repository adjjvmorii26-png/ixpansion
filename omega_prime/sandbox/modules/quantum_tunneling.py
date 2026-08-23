"""Quantum tunneling — agents can pass through impassable barriers.

Each barrier has a tunneling probability based on:
- Barrier "thickness" (how many attempts needed)
- How many other agents have tried (collective observation weakens barrier)
- Agent's curiosity trait

Successful tunneling permanently weakens the barrier for everyone.
This models how social barriers erode as more people challenge them.
"""
from __future__ import annotations

import hashlib
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Barrier:
    """An impassable obstacle between two regions."""

    barrier_id: str
    position: tuple[float, float]
    thickness: float          # Higher = harder to tunnel through
    total_attempts: int = 0
    successful_tunnels: int = 0
    integrity: float = 1.0    # 1=solid, 0=dissolved

    @property
    def base_tunnel_probability(self) -> float:
        """Base chance of tunneling through."""
        return max(0.001, 1.0 / self.thickness)

    @property
    def collective_boost(self) -> float:
        """More attempts weaken the barrier for everyone."""
        return min(0.5, self.total_attempts * 0.01)

    @property
    def current_probability(self) -> float:
        return min(0.95, self.base_tunnel_probability + self.collective_boost)


class TunnelingField:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._barriers: dict[str, Barrier] = {}
        self._tunnel_events: list[dict[str, Any]] = []

    def create_barrier(self, pos: tuple[float, float],
                       thickness: float = 10.0) -> str:
        bid = hashlib.sha256(f"{pos}:{thickness}".encode()).hexdigest()[:10]
        self._barriers[bid] = Barrier(barrier_id=bid, position=pos, thickness=thickness)
        return bid

    def attempt_tunnel(self, agent_id: str, agent_curiosity: float,
                       barrier_id: str) -> dict[str, Any]:
        """Try to pass through a barrier."""
        barrier = self._barriers.get(barrier_id)
        if not barrier or barrier.integrity <= 0.05:
            return {"success": True, "reason": "barrier_dissolved"}

        barrier.total_attempts += 1
        probability = min(0.95,
            barrier.current_probability * (1.0 + agent_curiosity * 0.3))

        success = self._rng.random() < probability

        if success:
            barrier.successful_tunnels += 1
            # Each successful tunnel weakens the barrier permanently
            barrier.integrity -= 0.08
            event = {
                "agent": agent_id[:8], "barrier": barrier_id[:8],
                "success": True, "probability": round(probability, 4),
                "integrity_remaining": round(barrier.integrity, 4),
                "total_attempts": barrier.total_attempts,
                "message": f"Tunneled through! Barrier weakened to {barrier.integrity:.0%}",
            }
        else:
            event = {
                "agent": agent_id[:8], "barrier": barrier_id[:8],
                "success": False, "probability": round(probability, 4),
                "message": "Failed to tunnel. Barrier holds... for now.",
            }

        self._tunnel_events.append(event)
        return event

    def tick_decay(self) -> int:
        """Barriers naturally repair if left alone."""
        repaired = 0
        for b in self._barriers.values():
            if b.integrity < 1.0 and self._rng.random() < 0.02:
                b.integrity = min(1.0, b.integrity + 0.01)
                repaired += 1
        return repaired

    @property
    def weakest_barrier(self) -> dict[str, Any] | None:
        active = [b for b in self._barriers.values() if b.integrity > 0]
        if not active:
            return None
        weakest = min(active, key=lambda b: b.integrity)
        return {
            "id": weakest.barrier_id[:8], "integrity": round(weakest.integrity, 3),
            "attempts": weakest.total_attempts, "tunnels": weakest.successful_tunnels,
            "current_probability": round(weakest.current_probability, 4),
        }

    @property
    def stats(self) -> dict[str, Any]:
        dissolved = sum(1 for b in self._barriers.values() if b.integrity <= 0.05)
        total_attempts = sum(b.total_attempts for b in self._barriers.values())
        total_tunnels = sum(b.successful_tunnels for b in self._barriers.values())
        avg_integrity = sum(b.integrity for b in self._barriers.values()) / max(len(self._barriers), 1)
        return {
            "barriers": len(self._barriers),
            "dissolved": dissolved,
            "avg_integrity": round(avg_integrity, 4),
            "total_attempts": total_attempts,
            "successful_tunnels": total_tunnels,
            "tunnel_rate": round(total_tunnels / max(total_attempts, 1), 4),
        }
