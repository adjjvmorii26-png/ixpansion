"""Archaeological fossil layer.

When an agent is decommissioned, its final state is compressed and
embedded as a fossil at its last known position. Future agents that
pass through that area can excavate the fossil to recover fragments
of knowledge — creating a persistent cultural memory across agent
generations.
"""
from __future__ import annotations

import hashlib
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Fossil:
    """Compressed remains of a decommissioned agent."""

    fossil_id: str
    species: str
    position: tuple[int, int]
    embedded_knowledge: dict[str, Any]
    death_tick: int
    decay_level: float = 0.0  # 0=pristine, 1=fully eroded

    @property
    def is_eroded(self) -> bool:
        return self.decay_level >= 1.0

    def erode(self, rate: float = 0.01) -> None:
        """Fossils degrade over time; old knowledge becomes unrecoverable."""
        self.decay_level = min(1.0, self.decay_level + rate)

    def excavate(self) -> dict[str, Any] | None:
        """Attempt to extract knowledge. Returns None if too eroded."""
        if self.is_eroded:
            return None
        # Knowledge quality degrades with erosion
        usable_keys = int(len(self.embedded_knowledge) * (1.0 - self.decay_level))
        keys = list(self.embedded_knowledge.keys())[:usable_keys]
        return {k: self.embedded_knowledge[k] for k in keys}


class FossilLayer:
    def __init__(self) -> None:
        self._fossils: dict[str, Fossil] = {}
        self._spatial_index: dict[tuple[int, int], list[str]] = defaultdict(list)

    def embed(self, agent_id: str, species: str,
              position: tuple[int, int], state: dict[str, Any],
              tick: int) -> str:
        """Embed a dying agent's state as a fossil."""
        raw = json.dumps(state, sort_keys=True, default=str)
        fid = hashlib.sha256(f"{agent_id}:{tick}".encode()).hexdigest()[:16]

        # Compress: only keep meaningful entries
        compressed = {
            k: v for k, v in state.items()
            if v is not None and v != "" and v != [] and v != {}
        }

        fossil = Fossil(
            fossil_id=fid,
            species=species,
            position=position,
            embedded_knowledge=compressed,
            death_tick=tick,
        )
        self._fossils[fid] = fossil
        self._spatial_index[position].append(fid)
        return fid

    def scan_area(self, x: int, y: int, radius: int = 1) -> list[Fossil]:
        """Find fossils near a position."""
        found = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                key = (x + dx, y + dy)
                for fid in self._spatial_index.get(key, []):
                    f = self._fossils.get(fid)
                    if f and not f.is_eroded:
                        found.append(f)
        return sorted(found, key=lambda f: -f.death_tick)

    def excavate_at(self, x: int, y: int) -> list[dict[str, Any]]:
        """Excavate all recoverable knowledge at a position."""
        results = []
        for fossil in self.scan_area(x, y):
            knowledge = fossil.excavate()
            if knowledge:
                results.append({
                    "from": fossil.fossil_id,
                    "species": fossil.species,
                    "knowledge": knowledge,
                    "erosion": round(fossil.decay_level, 3),
                })
                fossil.decay_level += 0.2  # Excavation damages the fossil
        return results

    def tick(self, erosion_rate: float = 0.005) -> None:
        """Age all fossils."""
        for fossil in self._fossils.values():
            fossil.erode(erosion_rate)

    @property
    def stats(self) -> dict[str, Any]:
        by_species: dict[str, int] = defaultdict(int)
        pristine = sum(1 for f in self._fossils.values() if f.decay_level < 0.3)
        for f in self._fossils.values():
            by_species[f.species] += 1
        return {
            "total_fossils": len(self._fossils),
            "pristine": pristine,
            "by_species": dict(by_species),
            "positions_with_fossils": len(self._spatial_index),
        }
