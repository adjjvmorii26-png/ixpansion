"""Reality bleed — boundary hybridization between contradictory truths.

When two adjacent cells have been consolidated to mutually exclusive
states (e.g., "forest" vs "void"), the boundary between them develops
a hybrid zone. Agents standing in the bleed experience properties of
both realities simultaneously. Prolonged exposure causes identity
blending: the agent's own classification becomes ambiguous.

Over time, bleeds either widen (consuming both parent cells) or heal
(one truth dominates and erases the other at the boundary).
"""
from __future__ import annotations

import hashlib
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BleedZone:
    """A hybrid reality between two contradictory cells."""

    bleed_id: str
    cell_a: tuple[int, int]
    cell_b: tuple[int, int]
    truth_a: str
    truth_b: str
    intensity: float = 0.1     # How strongly the hybrid manifests
    age: int = 0

    @property
    def hybrid_label(self) -> str:
        return f"{self.truth_a[:4]}~{self.truth_b[:4]}"

    @property
    def is_stable(self) -> bool:
        """Stable bleeds persist; unstable ones resolve."""
        return self.intensity >= 0.5

    def grow(self, amount: float = 0.05) -> None:
        self.intensity = min(1.0, self.intensity + amount)
        self.age += 1

    def heal(self, dominant_truth: str) -> str:
        """One reality wins; the bleed closes."""
        self.intensity = 0.0
        return dominant_truth


class RealityBleedEngine:
    GROWTH_RATE = 0.03
    HEAL_PROBABILITY = 0.05
    MAX_BLEEDS = 50

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._consolidated: dict[tuple[int, int], str] = {}  # pos -> truth
        self._bleeds: dict[str, BleedZone] = {}
        self._exposure_log: list[dict[str, Any]] = []

    def consolidate(self, pos: tuple[int, int], truth: str) -> list[dict[str, Any]]:
        """Set a cell's truth; check for new bleeds with neighbors."""
        old = self._consolidated.get(pos)
        self._consolidated[pos] = truth
        new_bleeds = []

        if old is not None and old != truth:
            # Truth changed — existing bleeds may destabilize
            pass

        # Check all four neighbors for contradictions
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            neighbor_pos = (pos[0]+dx, pos[1]+dy)
            neighbor_truth = self._consolidated.get(neighbor_pos)

            if neighbor_truth and neighbor_truth != truth:
                bid = hashlib.sha256(f"{pos}:{neighbor_pos}".encode()).hexdigest()[:10]
                if bid not in self._bleeds:
                    bleed = BleedZone(
                        bleed_id=bid, cell_a=pos, cell_b=neighbor_pos,
                        truth_a=truth, truth_b=neighbor_truth,
                    )
                    self._bleeds[bid] = bleed
                    new_bleeds.append({
                        "bleed_id": bid[:8],
                        "between": [truth, neighbor_truth],
                        "cells": [list(pos), list(neighbor_pos)],
                        "hybrid": bleed.hybrid_label,
                    })

        return new_bleeds

    def tick(self) -> dict[str, Any]:
        """Grow/heal bleeds each tick."""
        healed = []
        grew = 0

        for bid, bleed in list(self._bleeds.items()):
            if bleed.is_stable or self._rng.random() < 0.7:
                bleed.grow(self.GROWTH_RATE)
                grew += 1
            else:
                winner = self._rng.choice([bleed.truth_a, bleed.truth_b])
                bleed.heal(winner)
                healed.append({
                    "bleed_id": bid[:8],
                    "resolved_to": winner,
                    "age": bleed.age,
                })
                del self._bleeds[bid]

        # Cap total bleeds (oldest die first)
        if len(self._bleeds) > self.MAX_BLEEDS:
            oldest = sorted(self._bleeds.values(), key=lambda b: -b.age)[:len(self._bleeds) - self.MAX_BLEEDS]
            for b in oldest:
                del self._bleeds[b.bleed_id]

        return {
            "active_bleeds": len(self._bleeds),
            "grew": grew,
            "healed": len(healed),
            "healed_details": healed[:3],
        }

    def get_hybrid_at(self, pos: tuple[int, int]) -> str | None:
        """If this position is inside a bleed zone, return the hybrid label."""
        for bleed in self._bleeds.values():
            if pos in (bleed.cell_a, bleed.cell_b):
                return bleed.hybrid_label
        return None

    def expose_agent(self, agent_id: str, pos: tuple[int, int]) -> dict[str, Any]:
        """Agent stands in/near a bleed; experiences hybrid reality."""
        hybrid = self.get_hybrid_at(pos)
        if not hybrid:
            return {"affected": False}

        self._exposure_log.append({"agent": agent_id, "hybrid": hybrid, "tick": len(self._exposure_log)})
        return {
            "affected": True,
            "hybrid_reality": hybrid,
            "total_exposures": sum(1 for e in self._exposure_log if e["agent"] == agent_id),
        }

    @property
    def stats(self) -> dict[str, Any]:
        by_pair = defaultdict(int)
        for b in self._bleeds.values():
            by_pair[b.hybrid_label] += 1
        avg_intensity = sum(b.intensity for b in self._bleeds.values()) / max(len(self._bleeds), 1)
        return {
            "consolidated_cells": len(self._consolidated),
            "active_bleeds": len(self._bleeds),
            "avg_intensity": round(avg_intensity, 4),
            "unique_hybrids": len(by_pair),
            "topology": dict(by_pair),
        }
