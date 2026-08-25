#!/usr/bin/env python3
"""Negative Space Cartographer — map what isn't there.

Bridges negative_space + emergent_cartography + memory_palace to
create a system that maps absences, gaps, and voids in a world state.

Where emergent_cartography maps what agents have seen, this module
maps what they HAVEN'T seen — and reasons about why those gaps exist.
Gaps surrounded by high activity are "blind spots" (deliberately hidden).
Gaps in low-activity areas are "frontiers" (not yet explored).
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PresenceMap:
    """What is known to exist in the world."""
    width: int = 16
    height: int = 16
    cells: dict[tuple[int, int], str] = field(default_factory=dict)

    def set_cell(self, x: int, y: int, content: str) -> None:
        self.cells[(x, y)] = content

    def is_present(self, x: int, y: int) -> bool:
        return (x, y) in self.cells

    def activity_score(self, x: int, y: int, radius: int = 2) -> float:
        """How active the neighborhood of (x,y) is."""
        count = 0
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if (x + dx, y + dy) in self.cells:
                    count += 1
        total = (2 * radius + 1) ** 2
        return count / total


@dataclass
class Absence:
    position: tuple[int, int]
    category: str
    activity_neighbor: float
    depth: int  # How many neighbors are also absent
    pressure: float  # How "squeezed" this gap is
    reasoning: str

    def payload(self) -> dict[str, Any]:
        return {
            "position": list(self.position),
            "category": self.category,
            "activity_neighbor": round(self.activity_neighbor, 4),
            "depth": self.depth,
            "pressure": round(self.pressure, 4),
            "reasoning": self.reasoning,
        }


@dataclass
class NegativeSpaceCartographer:
    """Map absences in a world and classify them."""
    width: int = 16
    height: int = 16
    blind_spot_threshold: float = 0.6
    frontier_threshold: float = 0.2

    def scan(self, presence: PresenceMap) -> dict[str, Any]:
        absences: list[Absence] = []

        for y in range(self.height):
            for x in range(self.width):
                if presence.is_present(x, y):
                    continue

                activity = presence.activity_score(x, y)
                absent_neighbors = 0
                present_neighbors = 0
                for dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx[0], y + dx[1]
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if presence.is_present(nx, ny):
                            present_neighbors += 1
                        else:
                            absent_neighbors += 1

                depth = absent_neighbors
                pressure = present_neighbors / max(1, present_neighbors + absent_neighbors)

                if activity > self.blind_spot_threshold and pressure > 0.5:
                    category = "blind_spot"
                    reasoning = "High activity nearby but cell is empty — possibly deliberately hidden"
                elif activity < self.frontier_threshold and depth >= 2:
                    category = "deep_frontier"
                    reasoning = "Remote from all known content — unexplored territory"
                elif pressure > 0.7:
                    category = "compressed_gap"
                    reasoning = "Surrounded by content on most sides — anomaly"
                elif activity > 0.3:
                    category = "transition_zone"
                    reasoning = "Near moderate activity — likely a boundary"
                else:
                    category = "open_void"
                    reasoning = "Low surrounding activity — neutral emptiness"

                absences.append(Absence(
                    position=(x, y),
                    category=category,
                    activity_neighbor=activity,
                    depth=depth,
                    pressure=pressure,
                    reasoning=reasoning,
                ))

        categories: dict[str, int] = defaultdict(int)
        for a in absences:
            categories[a.category] += 1

        total_cells = self.width * self.height
        presence_ratio = len(presence.cells) / total_cells if total_cells else 0

        return {
            "total_absences": len(absences),
            "total_present": len(presence.cells),
            "presence_ratio": round(presence_ratio, 4),
            "categories": dict(categories),
            "notable_absences": [a.payload() for a in sorted(
                absences, key=lambda a: -a.pressure
            )[:10]],
            "void_signature": hashlib.sha256(
                json.dumps(sorted(categories.items())).encode()
            ).hexdigest()[:12],
        }


def demo() -> dict[str, Any]:
    world = PresenceMap(width=12, height=12)
    # Create a cluster of content with gaps
    for x in range(2, 10):
        for y in range(2, 10):
            if (x + y) % 3 != 0:  # Leave some gaps
                world.set_cell(x, y, "forest")
    # Dense center
    for x in range(4, 8):
        for y in range(4, 8):
            world.set_cell(x, y, "crystal")
    # Remove a cell from the dense center to create a blind spot
    world.cells.pop((5, 5), None)
    world.cells.pop((6, 6), None)

    cartographer = NegativeSpaceCartographer(width=12, height=12)
    return cartographer.scan(world)


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
