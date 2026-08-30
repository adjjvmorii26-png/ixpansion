#!/usr/bin/env python3
"""Stigmergy: coordination through environmental traces.

Ants build cities without speaking — they leave pheromone trails. This module
simulates stigmergic coordination where agents leave digital traces in a shared
environment. Other agents follow the trails, reinforcing successful paths and
letting unsuccessful ones evaporate.

This is the opposite of central planning. No single agent knows the plan.
The plan emerges from traces.

Usage:
    python3 stigmergy.py --agents 8 --steps 20 --seed 42
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from typing import Any, Dict, List, Tuple

TRAIL_DECAY = 0.85
TRAIL_STRENGTH = 1.0
EVAPORATION_THRESHOLD = 0.01


def _init_grid(width: int, height: int) -> Dict[Tuple[int, int], float]:
    """Initialize a pheromone grid (all zeros)."""
    return {(x, y): 0.0 for x in range(width) for y in range(height)}


def _deposit(grid: Dict[Tuple[int, int], float], x: int, y: int,
             width: int, height: int, strength: float = TRAIL_STRENGTH) -> None:
    """Deposit pheromone at a cell and adjacent cells (diffusion)."""
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            nx, ny = (x + dx) % width, (y + dy) % height
            dist = math.sqrt(dx * dx + dy * dy) or 0.5
            grid[(nx, ny)] = min(1.0, grid[(nx, ny)] + strength / dist)


def _evaporate(grid: Dict[Tuple[int, int], float]) -> None:
    """Evaporate all pheromone trails."""
    for key in grid:
        grid[key] *= TRAIL_DECAY
        if grid[key] < EVAPORATION_THRESHOLD:
            grid[key] = 0.0


def _move_toward_pheromone(grid: Dict[Tuple[int, int], float],
                           x: int, y: int, width: int, height: int,
                           rng: random.Random,
                           goal: Tuple[int, int] = None,
                           goal_sense: float = 3.0) -> Tuple[int, int]:
    """Agent moves toward pheromone + goal gradient + noise.

    The key insight of stigmergy: agents don't need to know the plan.
    They need a small bias (goal_sense) plus pheromone traces left by
    others. Early agents wander toward the goal, depositing strong
    pheromone. Later agents follow the trail faster.
    """
    candidates = []
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            nx, ny = (x + dx) % width, (y + dy) % height
            s = grid[(nx, ny)]
            # Combine pheromone strength with goal gradient
            if goal is not None:
                g = _goal_function(nx, ny, goal)
                s = s * 2.0 + g * goal_sense  # pheromone has 2x weight
            candidates.append(((dx, dy), s))

    chosen_dir, _ = rng.choices(candidates, weights=[c + 0.01 for _, c in candidates], k=1)[0]
    return (x + chosen_dir[0]) % width, (y + chosen_dir[1]) % height


def _goal_function(x: int, y: int, goal: Tuple[int, int]) -> float:
    """Proximity to goal — higher is better."""
    dx, dy = x - goal[0], y - goal[1]
    dist = math.sqrt(dx * dx + dy * dy)
    return 1.0 / (1.0 + dist)


def simulate(width: int = 20, height: int = 20, num_agents: int = 8,
             steps: int = 30, seed: int = 42, goal: Tuple[int, int] = None) -> Dict[str, Any]:
    """Run a stigmergic simulation.

    Agents start at random positions and attempt to reach a shared goal.
    They communicate only through pheromone traces.
    """
    rng = random.Random(seed)
    if goal is None:
        goal = (width - 1, height - 1)

    grid = _init_grid(width, height)
    agents = []
    for _ in range(num_agents):
        agents.append({
            "x": rng.randint(0, width - 1),
            "y": rng.randint(0, height - 1),
            "reached_goal": False,
            "trail_deposited": 0,
        })

    arrivals = []
    history = []

    for step in range(steps):
        # agents move
        for agent in agents:
            ax, ay = agent["x"], agent["y"]
            nx, ny = _move_toward_pheromone(grid, ax, ay, width, height, rng, goal=goal)

            # deposit trail at current position
            # Strength scales with proximity to goal (goal gradient)
            prox = _goal_function(ax, ay, goal)
            trail_strength = 0.2 + (prox * 1.8)  # 0.2 (far) to 2.0 (near goal)
            _deposit(grid, ax, ay, width, height, strength=trail_strength)
            agent["trail_deposited"] += 1

            agent["x"], agent["y"] = nx, ny

            # check if reached goal
            if not agent["reached_goal"] and _goal_function(nx, ny, goal) > 0.9:
                agent["reached_goal"] = True
                arrivals.append({"agent": len(arrivals), "step": step, "pos": (nx, ny)})

        # evaporate
        _evaporate(grid)

        # record state
        trail_sum = sum(grid.values())
        max_trail = max(grid.values()) if grid else 0
        reached = sum(1 for a in agents if a["reached_goal"])
        history.append({
            "step": step,
            "trails_active": sum(1 for v in grid.values() if v > EVAPORATION_THRESHOLD),
            "trail_energy": round(trail_sum, 2),
            "max_trail": round(max_trail, 4),
            "agents_at_goal": reached,
        })

    # compute final constellation: which cells were most visited
    hot_cells = sorted(grid.items(), key=lambda kv: -kv[1])[:10]
    path_map = [{"cell": list(c), "strength": round(s, 4)} for c, s in hot_cells if s > 0]

    return {
        "width": width,
        "height": height,
        "num_agents": num_agents,
        "steps": steps,
        "goal": list(goal),
        "agents_reached": sum(1 for a in agents if a["reached_goal"]),
        "arrivals": arrivals[:20],
        "hot_path": path_map[:10],
        "history": history,
        "philosophy": "No agent knows the plan. The plan emerges from pheromone traces. This is how ants build cities.",
    }


def main():
    ap = argparse.ArgumentParser(description="Stigmergy simulation")
    ap.add_argument("--width", type=int, default=15)
    ap.add_argument("--height", type=int, default=15)
    ap.add_argument("--agents", type=int, default=8)
    ap.add_argument("--steps", type=int, default=80)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    result = simulate(args.width, args.height, args.agents, args.steps, args.seed)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
