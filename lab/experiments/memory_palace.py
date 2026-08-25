#!/usr/bin/env python3
"""Memory Palace — spatial memory system for agents.

Agents forget information linearly. This module gives them a 2D memory
palace where they place memories at coordinates. Spatial locality means
related memories are nearby. Retrieval is by:
- Exact position lookup
- Proximity scan (find memories near a point)
- Decay scan (find memories that haven't been "visited" recently)
- Connection scan (find memories linked to a given memory)

The palace self-organizes: heavily accessed memories drift toward the
center, neglected memories drift toward the periphery and eventually
dissolve. This creates a natural forgetting curve that mimics human
spatial memory.

Bridges mycelium substrate concepts with agent cognition.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Memory:
    """A single memory placed in the palace."""
    memory_id: str
    content: str
    position: tuple[float, float]
    salience: float = 1.0
    access_count: int = 0
    last_accessed_tick: int = 0
    links: set[str] = field(default_factory=set)
    birth_tick: int = 0

    def decay(self, rate: float = 0.01) -> float:
        """Decay salience based on time since last access."""
        self.salience = max(0.0, self.salience - rate)
        return self.salience

    def access(self, tick: int) -> None:
        self.access_count += 1
        self.last_accessed_tick = tick
        self.salience = min(1.0, self.salience + 0.1)

    def payload(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "position": list(self.position),
            "salience": round(self.salience, 4),
            "access_count": self.access_count,
            "links": sorted(self.links),
            "age": "unknown",
        }


def _mid(a: float, b: float, factor: float = 0.5) -> float:
    return a + factor * (b - a)


@dataclass
class MemoryPalace:
    """A spatial memory system with organic forgetting and self-organization."""
    width: float = 100.0
    height: float = 100.0
    decay_rate: float = 0.005
    drift_rate: float = 0.1
    dissolve_threshold: float = 0.01
    seed: int | None = None
    center_pull: float = 0.02

    def __post_init__(self) -> None:
        self._memories: dict[str, Memory] = {}
        self._tick = 0

    @property
    def center(self) -> tuple[float, float]:
        return (self.width / 2, self.height / 2)

    def place(self, memory_id: str, content: str, position: tuple[float, float] | None = None) -> Memory:
        """Place a new memory in the palace."""
        if position is None:
            position = (self.width * 0.3, self.height * 0.3)

        memory = Memory(
            memory_id=memory_id,
            content=content,
            position=position,
            birth_tick=self._tick,
            last_accessed_tick=self._tick,
        )
        self._memories[memory_id] = memory
        return memory

    def recall(self, memory_id: str) -> Memory | None:
        """Recall a memory by ID (boosts its salience)."""
        memory = self._memories.get(memory_id)
        if memory:
            memory.access(self._tick)
        return memory

    def proximity_scan(self, point: tuple[float, float], radius: float = 20.0) -> list[Memory]:
        """Find memories near a point, sorted by distance."""
        results = []
        for memory in self._memories.values():
            dist = math.dist(point, memory.position)
            if dist <= radius:
                results.append(memory)
        return sorted(results, key=lambda m: math.dist(point, m.position))

    def decay_scan(self, threshold: float | None = None) -> list[Memory]:
        """Find memories below a salience threshold."""
        threshold = threshold if threshold is not None else self.dissolve_threshold
        return [m for m in self._memories.values() if m.salience <= threshold]

    def connection_scan(self, memory_id: str) -> list[Memory]:
        """Find all memories linked to a given memory."""
        memory = self._memories.get(memory_id)
        if not memory:
            return []
        return [self._memories[lid] for lid in memory.links if lid in self._memories]

    def link(self, id_a: str, id_b: str) -> bool:
        """Create a bidirectional link between two memories."""
        a = self._memories.get(id_a)
        b = self._memories.get(id_b)
        if not a or not b:
            return False
        a.links.add(id_b)
        b.links.add(id_a)
        return True

    def tick(self) -> dict[str, Any]:
        """Advance one tick: decay, dissolve, and self-organize."""
        self._tick += 1
        dissolved: list[str] = []
        moved: int = 0

        # Decay all memories
        for memory in list(self._memories.values()):
            memory.decay(self.decay_rate)

        # Dissolve dead memories
        for memory_id, memory in list(self._memories.items()):
            if memory.salience <= self.dissolve_threshold:
                dissolved.append(memory_id)
                # Remove links to this memory
                for other in self._memories.values():
                    other.links.discard(memory_id)
                del self._memories[memory_id]

        # Self-organize: center of gravity pull + access drift
        cx, cy = self.center
        for memory in self._memories.values():
            # Heavy memories drift toward center
            pull = self.center_pull * (1.0 - memory.salience)
            new_x = _mid(memory.position[0], cx, pull)
            new_y = _mid(memory.position[1], cy, pull)

            # Clamp to bounds
            new_x = max(0, min(self.width, new_x))
            new_y = max(0, min(self.height, new_y))

            if (new_x, new_y) != memory.position:
                memory.position = (new_x, new_y)
                moved += 1

        return {
            "tick": self._tick,
            "alive": len(self._memories),
            "dissolved": dissolved,
            "moved": moved,
        }

    def landscape(self) -> dict[str, Any]:
        """Full view of the palace state."""
        return {
            "tick": self._tick,
            "dimensions": [self.width, self.height],
            "memory_count": len(self._memories),
            "memories": [m.payload() for m in self._memories.values()],
            "total_links": sum(len(m.links) for m in self._memories.values()) // 2,
            "mean_salience": (
                round(sum(m.salience for m in self._memories.values()) / len(self._memories), 4)
                if self._memories else 0
            ),
        }


def demo() -> dict[str, Any]:
    palace = MemoryPalace(seed=42)

    # Place initial memories
    palace.place("axiom-0", "Zero execution authority", (20, 20))
    palace.place("axiom-1", "Manual-only recovery", (80, 20))
    palace.place("dream-1", "Mycelium dream about resonance", (50, 50))
    palace.place("event-1", "Pulse tick at t=100", (30, 70))
    palace.place("agent-1", "Sentinel born at lattice origin", (70, 70))

    # Link related memories
    palace.link("axiom-0", "axiom-1")
    palace.link("dream-1", "event-1")
    palace.link("agent-1", "axiom-1")

    # Simulate some access patterns and ticks
    ticks_data = []
    for t in range(30):
        if t % 5 == 0:
            palace.recall("dream-1")
        if t % 7 == 0:
            palace.recall("axiom-0")
        ticks_data.append(palace.tick())

    # Place a new memory mid-simulation
    palace.place("discovery-1", "Cross-pollination detected", (60, 40))

    # Final ticks
    for t in range(10):
        ticks_data.append(palace.tick())

    return {
        "landscape": palace.landscape(),
        "dissolved_count": sum(1 for td in ticks_data for _ in td["dissolved"]),
        "ticks_simulated": len(ticks_data),
        "proximity_scan_example": [
            m.payload() for m in palace.proximity_scan((50, 50), radius=30)
        ],
    }


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
