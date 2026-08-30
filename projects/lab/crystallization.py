#!/usr/bin/env python3
"""Crystallization — nucleation and growth from a supercooled liquid.

A crystal doesn't grow all at once. First, a tiny nucleus forms by chance.
Then it grows, following the crystal's internal structure. The process depends
on temperature, impurities, and the availability of seed sites.

This module simulates crystal nucleation and growth in a 2D lattice,
producing organic-looking crystal structures with branches, flaws, and
emergent patterns.

Usage:
    python3 crystallization.py --nuclei 3 --temperature 0.7 --seed 42
    python3 crystallization.py --nuclei 5 --temperature 0.5
"""
from __future__ import annotations

import argparse
import json
import math
import random
from typing import Any, Dict, List, Set, Tuple


# Crystal growth directions (4-connected + diagonals for branch spreading)
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
BRANCH_DIRS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def _crystal_hash(x: int, y: int, seed: int) -> float:
    """Deterministic pseudo-random for site nucleation probability."""
    return math.sin(x * 12.9898 + y * 78.233 + seed * 43.1234) * 43758.5453 % 1


def simulate(width: int = 30, height: int = 30, nuclei: int = 3,
             temperature: float = 0.7, growth_steps: int = 60,
             seed: int = 42) -> Dict[str, Any]:
    """Simulate crystal nucleation and growth.

    Args:
        width, height: lattice dimensions
        nuclei: number of seed nuclei
        temperature: 0=freeze (solid crystal), 1=melt (no growth)
        growth_steps: number of simulation steps
    """
    rng = random.Random(seed)
    lattice = {}  # (x,y) -> crystal_id
    frontier = set()  # (x,y) where crystal can grow into
    crystal_sizes = {}
    crystal_id_counter = 0

    # --- Phase 1: Nucleation ---
    for _ in range(nuclei):
        while True:
            x = rng.randint(1, width - 2)
            y = rng.randint(1, height - 2)
            if (x, y) not in lattice:
                lattice[(x, y)] = crystal_id_counter
                crystal_sizes[crystal_id_counter] = 1
                # Add neighbors to frontier
                for dx, dy in DIRECTIONS:
                    nx, ny = (x + dx) % width, (y + dy) % height
                    if (nx, ny) not in lattice:
                        frontier.add((nx, ny))
                crystal_id_counter += 1
                break

    # --- Phase 2: Growth ---
    growth_history = []
    for step in range(growth_steps):
        new_frontier = set()
        grown = 0
        for (x, y) in list(frontier):
            if (x, y) in lattice:
                continue
            # Check neighbors
            neighbor_crystals = {}
            for dx, dy in DIRECTIONS:
                nx, ny = (x + dx) % width, (y + dy) % height
                if (nx, ny) in lattice:
                    cid = lattice[(nx, ny)]
                    neighbor_crystals[cid] = neighbor_crystals.get(cid, 0) + 1

            if not neighbor_crystals:
                new_frontier.add((x, y))
                continue

            # Growth probability depends on neighbor count and temperature
            best_crystal = max(neighbor_crystals, key=neighbor_crystals.get)
            affinity = neighbor_crystals[best_crystal]
            growth_prob = min(1.0, (affinity / 2) * (1 - temperature * 0.8))
            # Temperature creates nucleation errors (wrong crystal)
            if temperature > 0.3 and _crystal_hash(x, y, step + seed) < temperature * 0.2:
                # nucleation error: new tiny crystal
                crystal_sizes[crystal_id_counter] = 0
                lattice[(x, y)] = crystal_id_counter
                crystal_id_counter += 1
            elif _crystal_hash(x, y, seed) < growth_prob:
                lattice[(x, y)] = best_crystal
                crystal_sizes[best_crystal] = crystal_sizes.get(best_crystal, 0) + 1
                grown += 1
                # Add new frontier
                for dx, dy in DIRECTIONS:
                    nx, ny = (x + dx) % width, (y + dy) % height
                    if (nx, ny) not in lattice:
                        new_frontier.add((nx, ny))
            else:
                new_frontier.add((x, y))

        frontier = new_frontier
        growth_history.append({"step": step, "crystals": len(crystal_sizes),
                              "grown": grown, "frontier": len(frontier)})

    # --- Analysis ---
    empty = sum(1 for x in range(width) for y in range(height) if (x, y) not in lattice)
    filled = width * height - empty
    crystal_list = [{"id": cid, "size": sz} for cid, sz in crystal_sizes.items()]
    crystal_list.sort(key=lambda c: -c["size"])

    # ASCII visualization
    ascii_art = []
    crystal_chars = list("abcdefghijklmnopqrstuvwxyz0123456789#@$%")
    for y in range(height):
        row = []
        for x in range(width):
            if (x, y) in lattice:
                cid = lattice[(x, y)]
                row.append(crystal_chars[cid % len(crystal_chars)])
            else:
                row.append(".")
        ascii_art.append(" ".join(row))

    return {
        "width": width,
        "height": height,
        "nuclei": nuclei,
        "temperature": temperature,
        "growth_steps": growth_steps,
        "filled_cells": filled,
        "empty_cells": empty,
        "fill_ratio": round(filled / (width * height), 3),
        "crystals": crystal_list[:10],
        "num_crystals": len(crystal_sizes),
        "largest_crystal": crystal_list[0] if crystal_list else None,
        "growth_history_sample": growth_history[::5],
        "ascii": ascii_art[:12],  # first 12 rows
        "philosophy": (
            "A crystal begins as a single uncertain molecule. Then it commits. "
            "Then it propagates its certainty outward. Every flaw is a memory "
            "of the moment the crystal hesitated."
        ),
    }


def main():
    ap = argparse.ArgumentParser(description="Crystallization simulation")
    ap.add_argument("--nuclei", type=int, default=3)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--steps", type=int, default=60)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--width", type=int, default=30)
    ap.add_argument("--height", type=int, default=30)
    args = ap.parse_args()
    result = simulate(args.width, args.height, args.nuclei, args.temperature,
                     args.steps, args.seed)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
