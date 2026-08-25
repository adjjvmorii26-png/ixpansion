#!/usr/bin/env python3
"""Reality Bleed Detector — identify when the system questions its own rules.

Bridges reality_bleed + ontological_collapse + consensus_reality to
detect and track contradictions in the world state. When two adjacent
regions hold mutually exclusive truths, a bleed zone forms. The detector
scans for these zones, classifies their severity, and predicts whether
they'll heal or widen.

This is the system's immune response to its own logical inconsistencies.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorldCell:
    position: tuple[int, int]
    truth: str
    confidence: float = 1.0
    consolidated_tick: int = 0

    def contrasts_with(self, other: "WorldCell") -> bool:
        return self.truth != other.truth and self.confidence > 0.5 and other.confidence > 0.5


@dataclass
class BleedZone:
    bleed_id: str
    cell_a: tuple[int, int]
    cell_b: tuple[int, int]
    truth_a: str
    truth_b: str
    intensity: float = 0.1
    age: int = 0
    agents_affected: set[str] = field(default_factory=set)
    resolved: bool = False
    winner: str | None = None

    @property
    def severity(self) -> str:
        if self.intensity >= 0.8:
            return "catastrophic"
        elif self.intensity >= 0.6:
            return "critical"
        elif self.intensity >= 0.4:
            return "significant"
        elif self.intensity >= 0.2:
            return "minor"
        return "negligible"

    @property
    def hybrid_label(self) -> str:
        return f"{self.truth_a[:4]}~{self.truth_b[:4]}"

    def grow(self, amount: float = 0.05) -> None:
        self.intensity = min(1.0, self.intensity + amount)
        self.age += 1

    def heal(self, winner_truth: str) -> None:
        self.resolved = True
        self.winner = winner_truth
        self.intensity = 0.0


@dataclass
class RealityBleedDetector:
    """Scans world state for reality contradictions."""
    width: int = 16
    height: int = 16
    grow_rate: float = 0.02
    heal_threshold: float = 0.9
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._world: dict[tuple[int, int], WorldCell] = {}
        self._bleeds: dict[str, BleedZone] = {}
        self._tick = 0
        self._scan_log: list[dict[str, Any]] = []

    def set_cell(self, x: int, y: int, truth: str, confidence: float = 1.0) -> None:
        self._world[(x, y)] = WorldCell(
            position=(x, y), truth=truth, confidence=confidence, consolidated_tick=self._tick
        )

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        new_bleeds: list[dict[str, Any]] = []
        healed: list[dict[str, Any]] = []

        # Scan for contradictions
        for pos, cell in self._world.items():
            for dx, dy in [(1, 0), (0, 1)]:
                neighbor_pos = (pos[0] + dx, pos[1] + dy)
                neighbor = self._world.get(neighbor_pos)
                if not neighbor or not cell.contrasts_with(neighbor):
                    continue

                bleed_key = self._bleed_key(pos, neighbor_pos)
                if bleed_key not in self._bleeds:
                    bleed = BleedZone(
                        bleed_id=hashlib.sha256(bleed_key.encode()).hexdigest()[:12],
                        cell_a=pos, cell_b=neighbor_pos,
                        truth_a=cell.truth, truth_b=neighbor.truth,
                    )
                    self._bleeds[bleed_key] = bleed
                    new_bleeds.append({
                        "bleed_id": bleed.bleed_id,
                        "truths": [cell.truth, neighbor.truth],
                        "position": [list(pos), list(neighbor_pos)],
                    })

        # Evolve existing bleeds
        for bleed_key, bleed in list(self._bleeds.items()):
            if bleed.resolved:
                continue
            bleed.grow(self.grow_rate * (1.0 + self._rng.random() * 0.5))

            # Heal only when one truth clearly dominates AND the bleed has aged
            a_cell = self._world.get(bleed.cell_a)
            b_cell = self._world.get(bleed.cell_b)
            if a_cell and b_cell and bleed.age > 3:
                conf_diff = abs(a_cell.confidence - b_cell.confidence)
                if conf_diff > 0.5:
                    winner = a_cell if a_cell.confidence > b_cell.confidence else b_cell
                    bleed.heal(winner.truth)
                    healed.append({"bleed_id": bleed.bleed_id, "winner": winner.truth})

        self._scan_log.append({
            "tick": self._tick,
            "new_bleeds": len(new_bleeds),
            "healed": len(healed),
            "active_bleeds": sum(1 for b in self._bleeds.values() if not b.resolved),
        })

        return {
            "tick": self._tick,
            "new_bleeds": new_bleeds,
            "healed": healed,
        }

    def scan_report(self) -> dict[str, Any]:
        active = [b for b in self._bleeds.values() if not b.resolved]
        resolved = [b for b in self._bleeds.values() if b.resolved]
        severity_dist = defaultdict(int)
        for b in active:
            severity_dist[b.severity] += 1

        return {
            "total_bleeds": len(self._bleeds),
            "active": len(active),
            "resolved": len(resolved),
            "severity_distribution": dict(severity_dist),
            "mean_intensity": round(
                sum(b.intensity for b in active) / max(1, len(active)), 4
            ),
            "oldest_bleed_age": max((b.age for b in active), default=0),
            "contradiction_pairs": [
                {
                    "id": b.bleed_id,
                    "truths": [b.truth_a, b.truth_b],
                    "severity": b.severity,
                    "intensity": round(b.intensity, 3),
                    "age": b.age,
                }
                for b in sorted(active, key=lambda x: -x.intensity)[:10]
            ],
        }

    def _bleed_key(self, a: tuple[int, int], b: tuple[int, int]) -> str:
        return f"{min(a, b)}:{max(a, b)}"

    def induce_collapse(self, x: int, y: int) -> dict[str, Any]:
        """Force a cell to change truth, potentially creating bleeds."""
        cell = self._world.get((x, y))
        if not cell:
            return {"status": "no_cell"}

        truths = ["forest", "void", "water", "crystal", "rock", "fire"]
        new_truth = self._rng.choice([t for t in truths if t != cell.truth])
        old_truth = cell.truth
        cell.truth = new_truth
        cell.confidence = 0.8
        cell.consolidated_tick = self._tick

        return {
            "status": "collapse",
            "old_truth": old_truth,
            "new_truth": new_truth,
            "position": [x, y],
            "tick": self._tick,
        }


def demo() -> dict[str, Any]:
    detector = RealityBleedDetector(seed=42)

    # Initialize a coherent world
    truths = [
        ["forest", "forest", "forest", "water", "water"],
        ["forest", "forest", "water", "water", "water"],
        ["forest", "rock", "rock", "void", "void"],
        ["rock", "rock", "void", "void", "crystal"],
        ["rock", "void", "void", "crystal", "crystal"],
    ]
    for y, row in enumerate(truths):
        for x, truth in enumerate(row):
            detector.set_cell(x, y, truth)

    # Tick to establish
    for _ in range(5):
        detector.tick()

    # Induce collapses to create contradictions
    detector.induce_collapse(1, 1)  # forest -> something else
    detector.induce_collapse(2, 2)  # rock -> something else
    detector.induce_collapse(3, 3)  # void -> something else

    # Scan and evolve
    for _ in range(15):
        detector.tick()

    return detector.scan_report()


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
