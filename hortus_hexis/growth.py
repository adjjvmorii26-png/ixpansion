"""Growth loop — a hex seed becomes a living organism.

Each organism is a set of cells on a small lattice. Growth follows
the genome: every cell reads the branch rule, heat phase, and
lethargy hold from its own byte and either branches, drops a seed
pod, or waits. The organism's final form is a top-down bitmap.
"""
from __future__ import annotations

import random
import time
from typing import Dict, List, Tuple

from .seed import genome_from_hex

Origin = Tuple[int, int]
Cell = Tuple[int, int, int]  # x, y, rule


class Organism:
    """A grown organism with a name, structure, and voice."""

    def __init__(self, name: str, seed: str, words: str, checked: int = 0):
        self.name = name
        self.seed = seed
        self.words = words
        self.box = _grow_box(seed)
        self.cells = self.box["cells"]
        self.vitality = self.box["vitality"]
        self.grown_ms = self.box["grown_ms"]
        self.checked = checked  # passes the harness gate (code + tests)

    def to_art(self) -> List[str]:
        return _render_box(self.box)

    def to_dict(self) -> Dict:
        return {
            "name": self.name, "seed": self.seed, "words": self.words,
            "cells": len(self.cells), "vitality": self.vitality,
            "grown_ms": self.grown_ms, "checked": self.checked,
        }


def _select_conditions(seed: str) -> Tuple[int, int, int]:
    """One growth environment from the seed: (depth, pods, patience)."""
    vals = [int(seed[i:i + 2], 16) for i in range(0, 16, 2) if seed[i:i + 2].isalnum()][0:4]
    vals = [v if v is not None else 7 for v in vals]
    depth = 1 + (vals[0] % 6) if len(vals) > 0 else 4
    pods = 1 + (vals[1] % 4) if len(vals) > 1 else 2
    patience = 1 + (vals[2] % 6) if len(vals) > 2 else 3
    return depth, pods, patience


def _grow_box(seed: str) -> Dict:
    genome = genome_from_hex(seed)
    rules = genome["rules"]
    depth, pods, patience = _select_conditions(seed)

    width = max(3, 11 + (len(rules) % 7))
    cells: List[Cell] = [(width // 2, 2, int(rules[0]) if rules else 0)]
    origin = (width // 2, 2)
    occupied = {origin}
    rng = random.Random(int(seed[:4], 16) if seed[:4].isalnum() else 42)

    growth = 1
    layer = [(origin)]
    for d in range(1, depth + 1):
        nxt = []
        for (x, y) in layer:
            if len(cells) > 96:
                break
            rule = rules[(x + y) % len(rules)] if rules else 0.0
            for ddx, ddy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                if rng.random() > 0.30:
                    nx, ny = x + ddx, y + ddy
                    if (nx, ny) not in occupied and 0 <= nx < width:
                        occupied.add((nx, ny))
                        cells.append((nx, ny, int(rule)))
                        nxt.append((nx, ny))
                        growth += 1
        layer = nxt
        if not layer:
            break

    pod_cells: List[Tuple[int, int]] = []
    for _ in range(pods):
        while True:
            cand = (rng.randrange(1, width - 1), rng.randrange(3, depth + 6))
            if cand in occupied:
                continue
            if 0 <= cand[0] < width:
                occupied.add(cand)
                cells.append((cand[0], cand[1], 0))
                pod_cells.append(cand)
                growth += 1
            break

    return {
        "cells": cells, "vitality": round(0.35 + growth / 50.0, 3),
        "grown_ms": round(rng.random() * 300 + 60, 1),
        "width": width, "depth": depth, "pod_count": len(pod_cells),
        "patience": patience,
    }


def _render_box(box: Dict, radius: int = 14) -> List[str]:
    cells = box["cells"]
    if not cells:
        return ["  .oOo.", "   HORT  "]
    cx = sum(c[0] for c in cells) / len(cells)
    cy = sum(c[1] for c in cells) / len(cells)
    half = int(radius)
    rows = []
    for row in range(-half, half + 1):
        line = ""
        for col in range(-half, half + 1):
            if any(abs(c[0] - cx - col) < 0.6 and abs(c[1] - cy - row) < 0.6 for c in cells):
                line += "@"
            else:
                line += "·"
        rows.append(line)
    return rows
