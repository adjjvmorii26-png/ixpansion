"""Gateways between dimensional spaces."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Portal:
    portal_id: str
    source_space: str
    dest_space: str
    anchor_a: tuple[float, ...]
    anchor_b: tuple[float, ...]
    stability: float = 1.0  # 1=solid, 0=collapsed
    toll_cost: float = 0.0  # Entropy cost to pass through
    created: float = field(default_factory=time.monotonic)

    @property
    def is_traversable(self) -> bool:
        return self.stability > 0.1

    def degrade(self, amount: float) -> None:
        self.stability = max(0.0, self.stability - amount)


class PortalNetwork:
    def __init__(self) -> None:
        self._portals: dict[str, Portal] = {}

    def open(self, src_space: str, dst_space: str,
             anchor_a: tuple[float, ...], anchor_b: tuple[float, ...],
             toll: float = 0.0) -> Portal:
        raw = f"{src_space}:{dst_space}:{anchor_a}:{anchor_b}"
        pid = hashlib.sha256(raw.encode()).hexdigest()[:12]
        portal = Portal(
            portal_id=pid, source_space=src_space, dest_space=dst_space,
            anchor_a=anchor_a, anchor_b=anchor_b, toll_cost=toll,
        )
        self._portals[pid] = portal
        return portal

    def find_route(self, from_space: str, to_space: str) -> list[str] | None:
        """BFS through portal network to find multi-hop route."""
        if from_space == to_space:
            return [from_space]

        adjacency: dict[str, list[tuple[str, str]]] = {}
        for p in self._portals.values():
            if p.is_traversable:
                adjacency.setdefault(p.source_space, []).append((p.dest_space, p.portal_id))
                adjacency.setdefault(p.dest_space, []).append((p.source_space, p.portal_id))

        visited = {from_space}
        queue = [(from_space, [])]
        while queue:
            current, path = queue.pop(0)
            for neighbor, pid in adjacency.get(current, []):
                if neighbor == to_space:
                    return path + [current, neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [current]))
        return None

    def tick_decay(self, rate: float = 0.005) -> int:
        collapsed = 0
        dead_ids = []
        for p in self._portals.values():
            p.degrade(rate)
            if not p.is_traversable:
                dead_ids.append(p.portal_id)
                collapsed += 1
        for pid in dead_ids:
            del self._portals[pid]
        return collapsed

    @property
    def open_portals(self) -> list[dict[str, Any]]:
        return [
            {"id": p.portal_id, "route": f"{p.source_space}→{p.dest_space}",
             "stability": round(p.stability, 3), "toll": p.toll_cost}
            for p in self._portals.values() if p.is_traversable
        ]
