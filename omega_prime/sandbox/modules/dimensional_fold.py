"""Dimensional fold — spatial topology mutator.

Periodically (or on command), the sandbox "folds" — bringing distant
grid cells adjacent while pushing previously-nearby cells apart.
Agents must continuously remap their mental model of space.

Folds are not teleportation; they change the adjacency structure.
Two cells that were 20 units apart might become neighbors after a fold.
"""
from __future__ import annotations

import hashlib
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FoldMapping:
    """A single cell-to-cell displacement caused by a fold event."""

    from_pos: tuple[int, int]
    to_pos: tuple[int, int]
    fold_id: str


class DimensionalFold:
    def __init__(self, width: int = 32, height: int = 32) -> None:
        self.width = width
        self.height = height
        self._fold_history: list[FoldMapping] = []
        self._active_folds: dict[str, list[tuple[tuple[int, int], tuple[int, int]]]] = {}
        self._fold_count = 0

    @property
    def topology_version(self) -> int:
        """Increments every time a fold changes adjacency."""
        return self._fold_count

    def fold(self, seed: int | None = None) -> str:
        """Perform a spatial fold: swap two non-overlapping regions."""
        rng = random.Random(seed)
        self._fold_count += 1
        fid = f"fold_{self._fold_count}_{hashlib.md5(str(seed).encode()).hexdigest()[:8]}"

        # Choose a horizontal or vertical split point
        if rng.random() > 0.5:
            # Horizontal fold: mirror rows around midpoint
            split = rng.randint(4, self.height - 4)
            swaps = []
            for y in range(split):
                mirrored_y = 2 * split - y - 1
                if 0 <= mirrored_y < self.height:
                    for x in range(self.width):
                        src = (x, y)
                        dst = (x, mirrored_y)
                        swaps.append((src, dst))
            self._active_folds[fid] = swaps
        else:
            # Vertical fold: mirror columns around midpoint
            split = rng.randint(4, self.width - 4)
            swaps = []
            for x in range(split):
                mirrored_x = 2 * split - x - 1
                if 0 <= mirrored_x < self.width:
                    for y in range(self.height):
                        src = (x, y)
                        dst = (mirrored_x, y)
                        swaps.append((src, dst))
            self._active_folds[fid] = swaps

        for src, dst in swaps:
            self._fold_history.append(FoldMapping(from_pos=src, to_pos=dst, fold_id=fid))

        return fid

    def resolve_position(self, pos: tuple[int, int]) -> tuple[int, int]:
        """Given a pre-fold position, compute post-fold position by applying all active folds in order."""
        current = pos
        for fid, swaps in self._active_folds.items():
            for src, dst in swaps:
                if current == src:
                    current = dst
                    break
        return current

    def unfold_last(self) -> bool:
        """Undo the most recent fold."""
        if not self._active_folds:
            return False
        last_fid = list(self._active_folds.keys())[-1]
        del self._active_folds[last_fid]
        return True

    def are_adjacent(self, a: tuple[int, int], b: tuple[int, int]) -> bool:
        """Check adjacency AFTER all folds are applied."""
        ra = self.resolve_position(a)
        rb = self.resolve_position(b)
        dx = abs(ra[0] - rb[0])
        dy = abs(ra[1] - rb[1])
        return (dx + dy) == 1  # Manhattan distance of 1

    @property
    def stats(self) -> dict[str, Any]:
        total_mappings = sum(len(v) for v in self._active_folds.values())
        return {
            "topology_version": self.topology_version,
            "active_folds": len(self._active_folds),
            "total_cell_swaps": total_mappings,
            "history_length": len(self._fold_history),
        }
