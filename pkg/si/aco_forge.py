#!/usr/bin/env python3
"""Ant Colony Optimization forge helper"""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class ACOConfig:
    n_ants: int = 12
    iters: int = 25
    alpha: float = 1.0
    beta: float = 2.0
    rho: float = 0.1
    q: float = 1.0
    seed: Optional[int] = None


@dataclass
class ACOResult:
    best_path: List[int]
    best_cost: float
    history: List[float] = field(default_factory=list)


class AntColony:
    def __init__(self, dist: List[List[float]], config: Optional[ACOConfig] = None):
        self.dist = dist
        self.n = len(dist)
        self.cfg = config or ACOConfig()
        self.rng = random.Random(self.cfg.seed)
        self.pher = [[1.0 for _ in range(self.n)] for _ in range(self.n)]

    def _tour(self, path: List[int]) -> float:
        return sum(self.dist[path[i]][path[i + 1]] for i in range(len(path) - 1))

    def optimize(self) -> ACOResult:
        best_path, best_cost = [], float("inf")
        history = []
        for _ in range(self.cfg.iters):
            paths = []
            for _a in range(self.cfg.n_ants):
                path = [self.rng.randrange(self.n)]
                while len(path) < self.n:
                    i = path[-1]
                    candidates = [j for j in range(self.n) if j not in path]
                    weights = []
                    for j in candidates:
                        tau = self.pher[i][j] ** self.cfg.alpha
                        eta = (1.0 / max(1e-9, self.dist[i][j])) ** self.cfg.beta
                        weights.append(tau * eta)
                    s = sum(weights) or 1.0
                    r = self.rng.random() * s
                    acc = 0.0
                    pick = candidates[-1]
                    for j, w in zip(candidates, weights):
                        acc += w
                        if acc >= r:
                            pick = j
                            break
                    path.append(pick)
                path.append(path[0])
                paths.append(path)
            for path in paths:
                c = self._tour(path)
                if c < best_cost:
                    best_cost, best_path = c, path[:]
            for i in range(self.n):
                for j in range(self.n):
                    self.pher[i][j] *= (1 - self.cfg.rho)
            for path in paths:
                c = self._tour(path)
                dep = self.cfg.q / max(1e-9, c)
                for a, b in zip(path[:-1], path[1:]):
                    self.pher[a][b] += dep
            history.append(best_cost)
        return ACOResult(best_path=best_path, best_cost=best_cost, history=history)
