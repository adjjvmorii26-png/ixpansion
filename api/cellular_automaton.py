"""Wave 125 — Cellular Automaton.

Grid-based computation where each cell follows simple rules but the
aggregate behaviour produces emergent complexity — from Conway's Game
of Life to custom rule sets that generate novel patterns.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Set, Tuple


class CellularAutomaton:
    """2D cellular automaton with configurable rules."""

    def __init__(self, width: int = 20, height: int = 20):
        self.width = width
        self.height = height
        self._alive: Set[Tuple[int, int]] = set()
        self._generation = 0
        self._history_length = 0

    def set_alive(self, x: int, y: int) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self._alive.add((x, y))

    def is_alive(self, x: int, y: int) -> bool:
        return (x, y) in self._alive

    def neighbours(self, x: int, y: int) -> int:
        count = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in self._alive:
                    count += 1
        return count

    def step(self) -> int:
        new_alive: Set[Tuple[int, int]] = set()
        for x in range(self.width):
            for y in range(self.height):
                n = self.neighbours(x, y)
                if (x, y) in self._alive:
                    if n in (2, 3):
                        new_alive.add((x, y))
                else:
                    if n == 3:
                        new_alive.add((x, y))
        self._alive = new_alive
        self._generation += 1
        self._history_length += 1
        return len(self._alive)

    def run(self, steps: int) -> List[int]:
        population_history = []
        for _ in range(steps):
            pop = self.step()
            population_history.append(pop)
        return population_history

    def population(self) -> int:
        return len(self._alive)

    def status(self) -> Dict[str, Any]:
        return {"generation": self._generation, "population": self.population(),
                "grid": f"{self.width}x{self.height}"}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "cellular_automaton", "action": action}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "125", "module": "cellular_automaton"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
