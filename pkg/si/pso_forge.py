#!/usr/bin/env python3
"""PSO-backed Forge agent — Particle Swarm Optimization for Forge-role agents."""
from __future__ import annotations

import random
import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple


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


def rosenbrock(x: Sequence[float]) -> float:
    return sum(100.0 * (x[i+1] - x[i]**2)**2 + (1 - x[i])**2 for i in range(len(x)-1)) if len(x) > 1 else (1-x[0])**2


def ackley(x: Sequence[float]) -> float:
    n = len(x) or 1
    a, b, c = 20.0, 0.2, 2 * math.pi
    s1 = sum(xi*xi for xi in x) / n
    s2 = sum(math.cos(c*xi) for xi in x) / n
    return -a * math.exp(-b * math.sqrt(s1)) - math.exp(s2) + a + math.e


def rastrigin(x: Sequence[float]) -> float:
    a = 10.0
    return a * len(x) + sum(xi * xi - a * math.cos(2 * math.pi * xi) for xi in x)


class ParticleSwarm:
    def __init__(self, config: Optional[PSOConfig] = None, fitness: Optional[Callable[[List[float]], float]] = None):
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
        gbest = pbest[g_idx][:]
        gbest_f = pbest_f[g_idx]
        history = [gbest_f]

        for it in range(cfg.iters):
            if cfg.w_decay:
                cfg.w = max(cfg.w_min, cfg.w * 0.99)
            for i in range(cfg.n_particles):
                for d in range(cfg.dim):
                    r1, r2 = self.rng.random(), self.rng.random()
                    vel[i][d] = (
                        cfg.w * vel[i][d]
                        + cfg.c1 * r1 * (pbest[i][d] - pos[i][d])
                        + cfg.c2 * r2 * (gbest[d] - pos[i][d])
                    )
                    vel[i][d] = max(-cfg.v_max, min(cfg.v_max, vel[i][d]))
                    pos[i][d] = self._clamp(pos[i][d] + vel[i][d])
                f = self.fitness(pos[i])
                if f < pbest_f[i]:
                    pbest_f[i] = f
                    pbest[i] = pos[i][:]
                    if f < gbest_f:
                        gbest_f = f
                        gbest = pos[i][:]
            history.append(gbest_f)

        return PSOResult(
            best_x=[round(x, 6) for x in gbest],
            best_fitness=gbest_f,
            history=history,
            iters=cfg.iters,
            particles=cfg.n_particles,
        )


def forge_pso(
    fitness: Optional[Callable[[List[float]], float]] = None,
    config: Optional[PSOConfig] = None,
) -> Dict:
    swarm = ParticleSwarm(config=config, fitness=fitness or sphere)
    result = swarm.optimize()
    return {
        "optimizer": "PSO",
        "best_x": result.best_x,
        "best_fitness": result.best_fitness,
        "iters": result.iters,
        "particles": result.particles,
        "final_history": result.history[-5:],
        "improved": result.history[0] - result.best_fitness,
    }


if __name__ == "__main__":
    out = forge_pso(config=PSOConfig(dim=3, n_particles=20, iters=50, seed=42))
    print(out)
