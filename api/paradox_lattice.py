"""Paradox Lattice — a structured grid of contradictions that generates insight.

Unlike random paradoxes, the Paradox Lattice arranges contradictions in
a precise geometric structure. Adjacent paradoxes influence each other,
creating emergent insights at intersection points. The lattice is a
mathematical engine for creative breakthrough.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class ParadoxCell:
    def __init__(self, x: int, y: int, thesis: str, antithesis: str):
        self.x = x
        self.y = y
        self.thesis = thesis
        self.antithesis = antithesis
        self.tension = 0.5
        self.insights_generated: List[str] = []
        self.active = True

    def interact(self, neighbor_tension: float) -> Dict[str, Any]:
        self.tension = min(1.0, self.tension + neighbor_tension * 0.1)
        if self.tension > 0.8 and random.random() > 0.5:
            insight = f"At ({self.x},{self.y}): '{self.thesis}' meets '{self.antithesis}' → emergence"
            self.insights_generated.append(insight)
            return {"insight": insight, "tension": round(self.tension, 3)}
        return {"tension": round(self.tension, 3)}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": [self.x, self.y],
            "thesis": self.thesis,
            "antithesis": self.antithesis,
            "tension": round(self.tension, 3),
            "insights": len(self.insights_generated),
        }


class ParadoxLattice:
    def __init__(self, width: int = 4, height: int = 4):
        self.cells: Dict[Tuple[int, int], ParadoxCell] = {}
        self.tick_count = 0
        self.all_insights: List[Dict[str, Any]] = []

    def populate(self, pairs: List[Tuple[str, str]] = None) -> Dict[str, Any]:
        default_pairs = [
            ("order", "chaos"), ("creation", "destruction"), ("freedom", "determinism"),
            ("simplicity", "complexity"), ("unity", "diversity"), ("past", "future"),
            ("silence", "noise"), ("light", "darkness"), ("meaning", "absurdity"),
            ("growth", "decay"), ("knowledge", "ignorance"), ("hope", "despair"),
            ("self", "other"), ("logic", "intuition"), ("finite", "infinite"),
            ("stability", "change"),
        ]
        pairs = pairs or default_pairs
        idx = 0
        for x in range(4):
            for y in range(4):
                if idx < len(pairs):
                    t, a = pairs[idx]
                    self.cells[(x, y)] = ParadoxCell(x, y, t, a)
                    idx += 1
        return {"populated": len(self.cells)}

    def tick(self) -> Dict[str, Any]:
        self.tick_count += 1
        new_insights = []
        for (x, y), cell in self.cells.items():
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    neighbor = self.cells.get((x + dx, y + dy))
                    if neighbor:
                        result = cell.interact(neighbor.tension)
                        if "insight" in result:
                            new_insights.append(result)
                            self.all_insights.append({**result, "time": time.time()})
        return {"tick": self.tick_count, "new_insights": len(new_insights), "total_insights": len(self.all_insights)}

    def lattice_map(self) -> List[Dict[str, Any]]:
        return [cell.to_dict() for cell in self.cells.values()]

    def lattice_stats(self) -> Dict[str, Any]:
        total_tension = sum(c.tension for c in self.cells.values())
        return {
            "total_cells": len(self.cells),
            "tick": self.tick_count,
            "avg_tension": round(total_tension / max(len(self.cells), 1), 3),
            "total_insights": len(self.all_insights),
        }


_lattice = ParadoxLattice()


def paradox_lattice_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "populate":
        return _lattice.populate(payload.get("pairs"))
    elif action == "tick":
        return _lattice.tick()
    elif action == "map":
        return {"cells": _lattice.lattice_map()}
    elif action == "insights":
        return {"insights": _lattice.all_insights[-10:]}
    return {"status": "active", **_lattice.lattice_stats()}


handler = paradox_lattice_handler
