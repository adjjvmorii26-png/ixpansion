"""Dream sharing — collective hallucinations materialize as terrain.

When multiple agents enter dream state simultaneously in the same
realm, their individual dreams can overlap. Shared dream archetypes
(forest, ocean, city, void) accumulate "dream density." When density
exceeds a threshold, the hallucination crystallizes into real terrain
that persists after all dreamers wake.

The sandbox literally becomes what its sleepers collectively imagine.
"""
from __future__ import annotations

import random
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DreamSeed:
    """A fragment of a single agent's dream."""

    dreamer_id: str
    archetype: str          # forest, ocean, city, void, fire, crystal...
    intensity: float        # 0-1, how vividly they dream it
    position_hint: tuple[float, float] | None = None

    @property
    def weight(self) -> float:
        return max(0.0, min(1.0, self.intensity))


@dataclass
class SharedDream:
    """An emerging collective hallucination."""

    archetype: str
    center: tuple[float, float]
    density: float = 0.0       # Accumulated dream energy
    contributors: set[str] = field(default_factory=set)
    tick_started: int = 0
    materialized: bool = False

    @property
    def solidity(self) -> float:
        """How close to becoming real terrain."""
        return min(1.0, self.density / 5.0)  # Threshold at density=5


class DreamSharingNetwork:
    MATERIALIZATION_THRESHOLD = 5.0
    DECAY_RATE = 0.02

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._active_dreamers: dict[str, list[DreamSeed]] = defaultdict(list)
        self._shared_dreams: dict[str, SharedDream] = {}  # key=archetype:region
        self._materialized_terrain: dict[tuple[float, float], str] = {}
        self._tick = 0

    def enter_dream(self, agent_id: str, archetype: str,
                    intensity: float = 0.7,
                    position: tuple[float, float] | None = None) -> None:
        seed = DreamSeed(
            dreamer_id=agent_id, archetype=archetype,
            intensity=max(0.0, min(1.0, intensity)), position_hint=position,
        )
        self._active_dreamers[agent_id].append(seed)

        # Try to merge with existing shared dreams nearby
        self._attempt_merge(seed)

    def exit_dream(self, agent_id: str) -> None:
        self._active_dreamers.pop(agent_id, None)

    def _region_key(self, archetype: str, pos: tuple[float, float]) -> str:
        """Quantize position to create regional buckets."""
        region_x = int(pos[0] // 10) if pos else 0
        region_y = int(pos[1] // 10) if pos else 0
        return f"{archetype}:{region_x}:{region_y}"

    def _attempt_merge(self, seed: DreamSeed) -> None:
        pos = seed.position_hint or (self._rng.uniform(-50, 50), self._rng.uniform(-50, 50))
        rkey = self._region_key(seed.archetype, pos)

        if rkey not in self._shared_dreams:
            self._shared_dreams[rkey] = SharedDream(
                archetype=seed.archetype,
                center=pos,
                tick_started=self._tick,
            )

        dream = self._shared_dreams[rkey]
        dream.density += seed.weight
        dream.contributors.add(seed.dreamer_id)

    def tick(self) -> dict[str, Any]:
        """Advance dream physics; check for materialization events."""
        self._tick += 1

        # Active dreamers continue contributing density each tick
        for agent_id, seeds in self._active_dreamers.items():
            for seed in seeds:
                rkey = self._region_key(seed.archetype, seed.position_hint or (0, 0))
                if rkey in self._shared_dreams and not self._shared_dreams[rkey].materialized:
                    self._shared_dreams[rkey].density += seed.weight * 0.5

        materialized_this_tick = []

        for rkey, dream in list(self._shared_dreams.items()):
            if dream.materialized:
                continue

            dream.density -= self.DECAY_RATE * len(dream.contributors) ** -0.5

            if dream.solidity >= 1.0 and len(dream.contributors) >= 2:
                dream.materialized = True
                terrain_pos = (
                    round(dream.center[0]),
                    round(dream.center[1]),
                )
                self._materialized_terrain[terrain_pos] = f"dream_{dream.archetype}"
                materialized_this_tick.append({
                    "archetype": dream.archetype,
                    "position": list(terrain_pos),
                    "density": round(dream.density, 3),
                    "dreamers": sorted(dream.contributors),
                })

        # Clean up stale unmaterialized dreams
        stale = [k for k, d in self._shared_dreams.items()
                 if not d.materialized and d.density <= 0]
        for k in stale:
            del self._shared_dreams[k]

        return {
            "tick": self._tick,
            "active_dreams": len([d for d in self._shared_dreams.values() if not d.materialized]),
            "materialized_count": len(self._materialized_terrain),
            "new_materializations": materialized_this_tick,
        }

    @property
    def dreamscape(self) -> dict[str, Any]:
        forming = [
            {"archetype": d.archetype, "solidity": round(d.solidity, 3),
             "dreamers": len(d.contributors)}
            for d in self._shared_dreams.values() if not d.materialized
        ]
        return {
            "forming_dreams": sorted(forming, key=lambda x: -x["solidity"]),
            "realized_terrain": {f"{k[0]},{k[1]}": v for k, v in self._materialized_terrain.items()},
        }
