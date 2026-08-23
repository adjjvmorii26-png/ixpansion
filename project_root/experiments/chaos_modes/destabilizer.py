"""Destabilizer — systematically breaks stable configurations."""
from __future__ import annotations

import random
from typing import Any


class Destabilizer:
    """Targets the most ordered/stable parts of a system and disrupts them."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._disruptions = 0

    def destabilize(self, agents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Find the most similar agents (most stable cluster) and differentiate them."""
        if len(agents) < 2:
            return agents

        # Find pair with smallest trait distance
        min_dist = float("inf")
        pair = (0, 1)
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                dist = self._trait_distance(agents[i], agents[j])
                if dist < min_dist:
                    min_dist = dist
                    pair = (i, j)

        # Push them apart
        a, b = agents[pair[0]], agents[pair[1]]
        for key in set(a.get("traits", {}).keys()) | set(b.get("traits", {}).keys()):
            va = a.get("traits", {}).get(key, 0.5)
            vb = b.get("traits", {}).get(key, 0.5)
            mid = (va + vb) / 2
            if "traits" in a:
                a["traits"][key] = round(max(0.0, min(1.0, mid - 0.15)), 4)
            if "traits" in b:
                b["traits"][key] = round(max(0.0, min(1.0, mid + 0.15)), 4)

        self._disruptions += 1
        return agents

    def _trait_distance(self, a: dict[str, Any], b: dict[str, Any]) -> float:
        ta = a.get("traits", {})
        tb = b.get("traits", {})
        all_keys = set(ta.keys()) | set(tb.keys())
        return sum(abs(ta.get(k, 0.5) - tb.get(k, 0.5)) for k in all_keys)

    @property
    def total_disruptions(self) -> int:
        return self._disruptions
