#!/usr/bin/env python3
"""Proof Density Analyzer — map the distribution of proof events.

Bridges proof_garden + kintsugi_ledger + entropy to analyze where
proofs cluster, where they're sparse, and where the system is most
vulnerable to unverifiable states.

Creates a "proof heat map" showing which regions of the event space
have strong cryptographic coverage and which are exposed.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProofEvent:
    event_id: str
    category: str
    position: tuple[int, int]
    strength: float
    timestamp: int


@dataclass
class ProofDensityAnalyzer:
    """Analyze proof event distribution across a grid."""
    width: int = 16
    height: int = 16
    cell_size: int = 2
    vulnerability_threshold: float = 0.3

    def __post_init__(self) -> None:
        self._events: list[ProofEvent] = []

    def add_event(self, event: ProofEvent) -> None:
        self._events.append(event)

    def analyze(self) -> dict[str, Any]:
        if not self._events:
            return {"status": "no_events"}

        # Build density grid
        grid_cells = (self.width // self.cell_size, self.height // self.cell_size)
        density = [[0.0 for _ in range(grid_cells[0])] for _ in range(grid_cells[1])]
        strength_grid = [[0.0 for _ in range(grid_cells[0])] for _ in range(grid_cells[1])]
        category_count = defaultdict(int)

        for event in self._events:
            gx = min(event.position[0] // self.cell_size, grid_cells[0] - 1)
            gy = min(event.position[1] // self.cell_size, grid_cells[1] - 1)
            density[gy][gx] += 1
            strength_grid[gy][gx] += event.strength
            category_count[event.category] += 1

        # Find hot spots and cold spots
        hot_spots: list[dict[str, Any]] = []
        cold_spots: list[dict[str, Any]] = []
        vulnerable_cells: list[dict[str, Any]] = []

        max_density = max(max(row) for row in density) if any(any(row) for row in density) else 1

        for gy in range(grid_cells[1]):
            for gx in range(grid_cells[0]):
                cell_density = density[gy][gx]
                cell_strength = strength_grid[gy][gx]
                normalized = cell_density / max_density if max_density > 0 else 0
                avg_strength = cell_strength / cell_density if cell_density > 0 else 0

                cell_info = {
                    "cell": [gx, gy],
                    "density": round(cell_density, 2),
                    "avg_strength": round(avg_strength, 4),
                    "normalized_density": round(normalized, 4),
                }

                if normalized > 0.7:
                    hot_spots.append(cell_info)
                elif normalized < 0.1 and cell_density > 0:
                    cold_spots.append(cell_info)
                elif cell_density == 0:
                    vulnerable_cells.append({**cell_info, "reason": "no_proof_coverage"})

        # Compute coverage metrics
        total_cells = grid_cells[0] * grid_cells[1]
        covered_cells = sum(1 for gy in range(grid_cells[1])
                           for gx in range(grid_cells[0]) if density[gy][gx] > 0)
        coverage = covered_cells / total_cells if total_cells else 0

        # Entropy of the distribution
        flat_density = [density[gy][gx] for gy in range(grid_cells[1]) for gx in range(grid_cells[0])]
        total = sum(flat_density)
        if total > 0:
            probs = [d / total for d in flat_density if d > 0]
            entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        else:
            entropy = 0.0

        return {
            "total_events": len(self._events),
            "grid_size": list(grid_cells),
            "coverage": round(coverage, 4),
            "entropy": round(entropy, 4),
            "categories": dict(category_count),
            "hot_spots": sorted(hot_spots, key=lambda h: -h["density"])[:5],
            "cold_spots": sorted(cold_spots, key=lambda c: c["density"])[:5],
            "vulnerable_cells": len(vulnerable_cells),
            "vulnerability_ratio": round(len(vulnerable_cells) / total_cells, 4) if total_cells else 0,
            "proof_signature": hashlib.sha256(
                json.dumps({"events": len(self._events), "coverage": round(coverage, 4)}).encode()
            ).hexdigest()[:12],
        }


def demo() -> dict[str, Any]:
    analyzer = ProofDensityAnalyzer(width=16, height=16, cell_size=2)
    rng = random.Random(42)

    categories = ["consent", "transfer", "mutation", "repair", "ritual"]

    # Create clustered events
    clusters = [(3, 3), (10, 5), (7, 12)]
    for cx, cy in clusters:
        for _ in range(15):
            x = max(0, min(15, cx + rng.randint(-2, 2)))
            y = max(0, min(15, cy + rng.randint(-2, 2)))
            analyzer.add_event(ProofEvent(
                event_id=hashlib.sha256(f"{x}:{y}:{rng.random()}".encode()).hexdigest()[:8],
                category=rng.choice(categories),
                position=(x, y),
                strength=rng.uniform(0.3, 1.0),
                timestamp=rng.randint(1, 100),
            ))

    # Sparse events in corners
    for _ in range(5):
        x, y = rng.choice([(0, 0), (15, 0), (0, 15), (15, 15)])
        analyzer.add_event(ProofEvent(
            event_id=hashlib.sha256(f"sparse:{x}:{y}".encode()).hexdigest()[:8],
            category="transfer",
            position=(x, y),
            strength=rng.uniform(0.1, 0.5),
            timestamp=rng.randint(1, 100),
        ))

    return analyzer.analyze()


import random  # noqa: E402


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
