from __future__ import annotations
"""Soup of Life — Game of Life variant where cells have recipes.

Conway's Game of Life meets molecular gastronomy. Each cell has a
"recipe" (state vector) and can "cook" neighbors by transferring
energy/information. Cells that are overcooked die; undercooked cells
remain dormant. The soup self-organizes into stable "dishes."
"""
import math
import random
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class Cell:
    x: int
    y: int
    alive: bool = True
    recipe: List[float] = field(default_factory=list)
    heat: float = 0.5
    flavor: str = "neutral"
    age: int = 0

    def cook(self, heat_transfer: float = 0.1):
        self.heat = max(0.0, min(1.0, self.heat))
        self.age += 1
        if self.heat > 0.8:
            self.flavor = "burnt"
            self.alive = False
        elif self.heat < 0.2:
            self.flavor = "raw"
        elif 0.4 <= self.heat <= 0.6:
            self.flavor = "perfect"
        else:
            self.flavor = "cooked"

class SoupOfLife:
    def __init__(self, width: int = 30, height: int = 30, seed: int = 42):
        self.width = width
        self.height = height
        self.rng = random.Random(seed)
        self.grid: Dict[Tuple[int, int], Cell] = {}
        self.tick = 0
        self.history: List[Dict] = []

    def seed(self, density: float = 0.3):
        for x in range(self.width):
            for y in range(self.height):
                if self.rng.random() < density:
                    recipe = [self.rng.uniform(0, 1) for _ in range(3)]
                    self.grid[(x, y)] = Cell(
                        x=x, y=y, alive=True, recipe=recipe,
                        heat=self.rng.uniform(0.3, 0.7)
                    )

    def _neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = (x + dx) % self.width, (y + dy) % self.height
                neighbors.append((nx, ny))
        return neighbors

    def step(self):
        self.tick += 1
        new_grid: Dict[Tuple[int, int], Cell] = {}

        for (x, y), cell in self.grid.items():
            if not cell.alive:
                continue
            alive_neighbors = sum(
                1 for nx, ny in self._neighbors(x, y)
                if (nx, ny) in self.grid and self.grid[(nx, ny)].alive
            )
            heat_transfer = 0.0
            for nx, ny in self._neighbors(x, y):
                if (nx, ny) in self.grid:
                    heat_transfer += self.grid[(nx, ny)].heat * 0.05

            cell.heat += heat_transfer
            cell.cook()

            if cell.alive:
                if alive_neighbors < 2:
                    cell.alive = False
                elif alive_neighbors > 3:
                    cell.alive = False
                else:
                    new_grid[(x, y)] = cell

        for (x, y), cell in list(self.grid.items()):
            if not cell.alive:
                continue
            for nx, ny in self._neighbors(x, y):
                if (nx, ny) not in self.grid or not self.grid[(nx, ny)].alive:
                    alive_count = sum(
                        1 for nnx, nny in self._neighbors(nx, ny)
                        if (nnx, nny) in self.grid and self.grid[(nnx, nny)].alive
                    )
                    if alive_count == 3:
                        recipe = [self.rng.uniform(0, 1) for _ in range(3)]
                        new_grid[(nx, ny)] = Cell(
                            x=nx, y=ny, alive=True, recipe=recipe,
                            heat=0.5
                        )

        self.grid = new_grid
        alive_count = sum(1 for c in self.grid.values() if c.alive)
        flavors = {}
        for c in self.grid.values():
            if c.alive:
                flavors[c.flavor] = flavors.get(c.flavor, 0) + 1
        self.history.append({
            "tick": self.tick, "alive": alive_count,
            "flavors": flavors,
        })

    def run(self, ticks: int = 20) -> List[Dict]:
        for _ in range(ticks):
            self.step()
        return self.history

    def dish_report(self) -> Dict:
        alive = [c for c in self.grid.values() if c.alive]
        flavors = {}
        for c in alive:
            flavors[c.flavor] = flavors.get(c.flavor, 0) + 1
        avg_heat = sum(c.heat for c in alive) / max(len(alive), 1)
        return {
            "cells_alive": len(alive),
            "flavors": flavors,
            "avg_heat": round(avg_heat, 3),
            "tick": self.tick,
        }


def demo():
    soup = SoupOfLife(width=20, height=20, seed=42)
    print("=== Soup of Life ===")
    soup.seed(density=0.3)
    initial = len([c for c in soup.grid.values() if c.alive])
    print(f"  Seeded: {initial} cells")

    history = soup.run(ticks=15)
    report = soup.dish_report()
    print(f"  After 15 ticks: {report['cells_alive']} cells alive")
    print(f"  Flavors: {report['flavors']}")
    print(f"  Avg heat: {report['avg_heat']}")

    return report


if __name__ == "__main__":
    demo()
