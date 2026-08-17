#!/usr/bin/env python3
"""PSO-backed Forge agent"""
from __future__ import annotations
import random, math
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence, Tuple


@dataclass
class PSOConfig:
    dim: int = 4
    n_particles: int = 16
    iters: int = 40
    w: float = 0.72
    c1: float = 1.4
    c2: float = 1.4
    v_max: float = 0.5
    bounds: Tuple[float, float] = (-5.0, 5.0)
    seed: Optional[int] = None
    w_decay: bool = True
    w_min: float = 0.4


@dataclass
class PSOResult:
    best_x: List[float]
    best_fitness: float
    history: List[float] = field(default_factory=list)
    iters: int = 0
    particles: int = 0


def sphere(x: Sequence[float]) -> float:
    return sum(xi * xi for xi in x)


class ParticleSwarm:
    def __init__(self, config: Optional[PSOConfig] = None, fitness: Optional[Callable] = None):
        self.cfg = config or PSOConfig()
        self.fitness = fitness or sphere
        self.rng = random.Random(self.cfg.seed)

    def _clamp(self, x: float) -> float:
        lo, hi = self.cfg.bounds
        return max(lo, min(hi, x))

    def optimize(self) -> PSOResult:
        cfg = self.cfg
        lo, hi = cfg.bounds
        pos = [[self.rng.uniform(lo, hi) for _ in range(cfg.dim)] for _ in range(cfg.n_particles)]
        vel = [[self.rng.uniform(-cfg.v_max, cfg.v_max) for _ in range(cfg.dim)] for _ in range(cfg.n_particles)]
        pbest = [p[:] for p in pos]
        pbest_f = [self.fitness(p) for p in pbest]
        g_idx = min(range(cfg.n_particles), key=lambda i: pbest_f[i])
        gbest, gbest_f = pbest[g_idx][:], pbest_f[g_idx]
        history = [gbest_f]
        for it in range(cfg.iters):
            w = cfg.w
            if cfg.w_decay:
                w = cfg.w_min + (cfg.w - cfg.w_min) * (1 - it / max(1, cfg.iters - 1))
            for i in range(cfg.n_particles):
                for d in range(cfg.dim):
                    r1, r2 = self.rng.random(), self.rng.random()
                    vel[i][d] = (
                        w * vel[i][d]
                        + cfg.c1 * r1 * (pbest[i][d] - pos[i][d])
                        + cfg.c2 * r2 * (gbest[d] - pos[i][d])
                    )
                    vel[i][d] = max(-cfg.v_max, min(cfg.v_max, vel[i][d]))
                    pos[i][d] = self._clamp(pos[i][d] + vel[i][d])
                f = self.fitness(pos[i])
                if f < pbest_f[i]:
                    pbest[i], pbest_f[i] = pos[i][:], f
                    if f < gbest_f:
                        gbest, gbest_f = pos[i][:], f
            history.append(gbest_f)
        return PSOResult(best_x=gbest, best_fitness=gbest_f, history=history, iters=cfg.iters, particles=cfg.n_particles)


def run_pso_sphere(seed: int = 0) -> dict:
    r = ParticleSwarm(PSOConfig(seed=seed, iters=30, n_particles=12)).optimize()
    return {"best_fitness": r.best_fitness, "best_x": r.best_x, "iters": r.iters}
