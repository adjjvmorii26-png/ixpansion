#!/usr/bin/env python3
"""Fractal Reactor Grid — self-similar reactor system that scales with load.

A grid of reactor cells where each cell can subdivide into sub-cells
when load increases, or merge back when load decreases. The grid is
fractal: each sub-cell has the same structure as the parent, creating
self-similar patterns at every scale.

High-load zones automatically create finer-grained reactors,
while low-load zones coalesce into coarser ones. This creates
"fractal hot-zones" where innovation density is highest.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReactorCell:
    cell_id: str
    position: tuple[int, int]
    load: float = 0.0
    capacity: float = 1.0
    subdivision_level: int = 0
    children: list[str] = field(default_factory=list)
    parent: str | None = None
    entropy: float = 0.5

    @property
    def utilization(self) -> float:
        return min(1.0, self.load / max(0.01, self.capacity))

    @property
    def should_subdivide(self) -> bool:
        return self.utilization > 0.8 and self.subdivision_level < 3

    @property
    def should_merge(self) -> bool:
        return self.utilization < 0.2 and self.children and self.subdivision_level > 0

    @property
    def is_leaf(self) -> bool:
        return not self.children

    def payload(self) -> dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "position": list(self.position),
            "load": round(self.load, 3),
            "utilization": round(self.utilization, 3),
            "level": self.subdivision_level,
            "children": len(self.children),
            "entropy": round(self.entropy, 3),
        }


@dataclass
class FractalReactorGrid:
    """Self-similar reactor grid that scales with load."""
    max_level: int = 3
    subdivision_threshold: float = 0.8
    merge_threshold: float = 0.2
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = __import__("random").Random(self.seed)
        self._cells: dict[str, ReactorCell] = {}
        self._tick = 0
        self._events: list[dict[str, Any]] = []
        self._next_id = 0

    def init_grid(self, width: int = 4, height: int = 4) -> None:
        for y in range(height):
            for x in range(width):
                cid = self._make_id()
                self._cells[cid] = ReactorCell(
                    cell_id=cid, position=(x, y),
                    capacity=self._rng.uniform(0.5, 1.5),
                )

    def _make_id(self) -> str:
        self._next_id += 1
        return f"cell_{self._next_id:04d}"

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        subdivisions = 0
        merges = 0

        # Apply load
        for cell in self._cells.values():
            if cell.is_leaf:
                cell.load = min(cell.capacity, cell.load + self._rng.uniform(-0.1, 0.2))
                cell.load = max(0.0, cell.load)
                cell.entropy = max(0.0, min(1.0, cell.entropy + self._rng.gauss(0, 0.05)))

        # Check subdivisions
        for cell in list(self._cells.values()):
            if cell.should_subdivide:
                self._subdivide(cell)
                subdivisions += 1

        # Check merges
        for cell in list(self._cells.values()):
            if cell.should_merge:
                self._merge(cell)
                merges += 1

        self._events.append({
            "tick": self._tick,
            "subdivisions": subdivisions,
            "merges": merges,
            "total_cells": len(self._cells),
        })

        return {"tick": self._tick, "subdivisions": subdivisions, "merges": merges}

    def _subdivide(self, cell: ReactorCell) -> None:
        """Split a cell into 4 sub-cells."""
        if cell.subdivision_level >= self.max_level:
            return

        x, y = cell.position
        offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]
        cell.load = 0.0
        cell.entropy = 0.0

        for dx, dy in offsets:
            child_id = self._make_id()
            child = ReactorCell(
                cell_id=child_id,
                position=(x * 2 + dx, y * 2 + dy),
                load=cell.capacity * 0.25,
                capacity=cell.capacity * 0.5,
                subdivision_level=cell.subdivision_level + 1,
                parent=cell.cell_id,
                entropy=cell.entropy,
            )
            self._cells[child_id] = child
            cell.children.append(child_id)

    def _merge(self, cell: ReactorCell) -> None:
        """Merge children back into parent."""
        for child_id in cell.children:
            if child_id in self._cells:
                child = self._cells[child_id]
                cell.load += child.load
                cell.entropy = max(cell.entropy, child.entropy)
                del self._cells[child_id]
        cell.children = []
        cell.subdivision_level = max(0, cell.subdivision_level - 1)

    def grid_report(self) -> dict[str, Any]:
        levels = defaultdict(int)
        total_load = 0.0
        leaves = 0
        for cell in self._cells.values():
            levels[cell.subdivision_level] += 1
            total_load += cell.load
            if cell.is_leaf:
                leaves += 1

        return {
            "tick": self._tick,
            "total_cells": len(self._cells),
            "leaf_cells": leaves,
            "levels": dict(levels),
            "total_load": round(total_load, 3),
            "mean_entropy": round(
                sum(c.entropy for c in self._cells.values()) / max(1, len(self._cells)), 3
            ),
            "events": len(self._events),
        }


def demo() -> dict[str, Any]:
    grid = FractalReactorGrid(seed=42)
    grid.init_grid(3, 3)
    for _ in range(20):
        grid.tick()
    return grid.grid_report()


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
