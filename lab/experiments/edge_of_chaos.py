from __future__ import annotations
"""Edge of Chaos — finds optimal complexity between order and chaos.

Like cellular automata that are most interesting at the edge between
ordered and chaotic behavior (Wolfram's Class IV), this module measures
system complexity and finds the sweet spot where computation is maximized.
"""
import math
import random
import json
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ComplexityState:
    order: float = 0.5
    chaos: float = 0.5
    complexity: float = 0.0
    computation: float = 0.0

class EdgeOfChaosFinder:
    def __init__(self, grid_size: int = 20, seed: int = 42):
        self.grid_size = grid_size
        self.rng = random.Random(seed)
        self.grid: List[List[int]] = []
        self.states: List[ComplexityState] = []

    def _init_grid(self, density: float = 0.5):
        self.grid = [
            [1 if self.rng.random() < density else 0
             for _ in range(self.grid_size)]
            for _ in range(self.grid_size)
        ]

    def _step(self, rule: int = 110):
        new_grid = [row[:] for row in self.grid]
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                left = self.grid[i][(j - 1) % self.grid_size]
                center = self.grid[i][j]
                right = self.grid[i][(j + 1) % self.grid_size]
                pattern = (left << 2) | (center << 1) | right
                new_grid[i][j] = (rule >> pattern) & 1
        self.grid = new_grid

    def _measure(self) -> ComplexityState:
        flat = [self.grid[i][j] for i in range(self.grid_size)
                for j in range(self.grid_size)]
        ones = sum(flat)
        total = len(flat)
        density = ones / total

        order = 1.0 - abs(density - 0.5) * 2

        transitions = 0
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] != self.grid[i][(j + 1) % self.grid_size]:
                    transitions += 1
        chaos = transitions / (total * 2)

        complexity = order * chaos * 4
        computation = complexity * (1 + chaos)

        return ComplexityState(
            order=order, chaos=chaos,
            complexity=complexity, computation=computation,
        )

    def find_edge(self, rules: List[int] = None, steps: int = 30) -> Dict:
        if rules is None:
            rules = [30, 45, 60, 90, 110, 150, 180, 210]

        best_rule = 0
        best_complexity = 0
        results = {}

        for rule in rules:
            self._init_grid(density=0.5)
            states = []
            for _ in range(steps):
                self._step(rule)
                state = self._measure()
                states.append(state)
            avg_complexity = sum(s.complexity for s in states) / len(states)
            avg_computation = sum(s.computation for s in states) / len(states)
            results[rule] = {
                "avg_complexity": round(avg_complexity, 4),
                "avg_computation": round(avg_computation, 4),
                "avg_order": round(sum(s.order for s in states) / len(states), 4),
                "avg_chaos": round(sum(s.chaos for s in states) / len(states), 4),
            }
            if avg_complexity > best_complexity:
                best_complexity = avg_complexity
                best_rule = rule

        return {
            "best_rule": best_rule,
            "best_complexity": round(best_complexity, 4),
            "rules_analyzed": len(rules),
            "results": results,
        }


def demo():
    finder = EdgeOfChaosFinder(grid_size=15, seed=42)
    print("=== Edge of Chaos Finder ===")
    result = finder.find_edge(steps=20)
    print(f"  Best rule: {result['best_rule']} "
          f"(complexity={result['best_complexity']})")
    print(f"  Rules analyzed: {result['rules_analyzed']}")
    for rule, metrics in sorted(result["results"].items(),
                                 key=lambda x: x[1]["avg_complexity"], reverse=True)[:5]:
        print(f"  Rule {rule}: complexity={metrics['avg_complexity']}, "
              f"order={metrics['avg_order']}, chaos={metrics['avg_chaos']}")
    return result


if __name__ == "__main__":
    demo()
