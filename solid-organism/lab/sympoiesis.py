#!/usr/bin/env python3
"""Sympoiesis: making-together.

Coral builds reefs. No single polyp designs the structure. Each contributes
a tiny calcium deposit, following local chemical gradients. The reef emerges.

This module simulates sympoietic collaboration: agents contribute "spores"
(building blocks) to a shared structure. The structure's emergent properties
(shape, density, coherence) are NOT present in any individual spore.

Usage:
    python3 sympoiesis.py --agents 12 --rounds 20 --seed 42
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import defaultdict
from typing import Any, Dict, List, Tuple


SPORE_TYPES = ["calcium", "silk", "prism", "echo", "void"]
SPORE_COLORS = {
    "calcium": "#e8e0d0",
    "silk": "#c0d0f0",
    "prism": "#f0c0e0",
    "echo": "#d0f0e0",
    "void": "#202030",
}


def _spore_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()[:8]


def _make_spore(agent_id: int, round_num: int, rng: random.Random) -> Dict[str, Any]:
    """An agent produces a spore — their building block contribution."""
    stype = rng.choice(SPORE_TYPES)
    weight = round(rng.uniform(0.3, 1.0), 3)
    resonance = round(rng.uniform(-1.0, 1.0), 3)
    return {
        "type": stype,
        "agent": agent_id,
        "round": round_num,
        "weight": weight,
        "resonance": resonance,
        "fingerprint": _spore_hash(f"{agent_id}:{round_num}:{stype}"),
    }


def _neighbor_influence(cell: Dict[str, Any], neighbors: List[Dict[str, Any]]) -> float:
    """A cell's weight shifts based on its neighbors (like crystal growth)."""
    if not neighbors:
        return 0.0
    same_type = sum(1 for n in neighbors if n.get("type") == cell.get("type"))
    resonance_avg = sum(n.get("resonance", 0) for n in neighbors) / len(neighbors)
    return (same_type / len(neighbors)) * 0.5 + resonance_avg * 0.5


def simulate(agents: int = 12, rounds: int = 20, seed: int = 42,
             grid_size: int = 20) -> Dict[str, Any]:
    """Run a sympoietic simulation.

    Each round, each agent places a spore on the grid.
    Spores interact with neighbors (influence each other's resonance).
    After all rounds, we measure emergent properties.
    """
    rng = random.Random(seed)
    grid: Dict[Tuple[int, int], List[Dict[str, Any]]] = defaultdict(list)
    agent_output: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    all_spores = []
    round_log = []

    for round_num in range(rounds):
        round_spores = []
        for agent_id in range(agents):
            spore = _make_spore(agent_id, round_num, rng)
            x = rng.randint(0, grid_size - 1)
            y = rng.randint(0, grid_size - 1)
            spore["pos"] = (x, y)
            grid[(x, y)].append(spore)
            agent_output[agent_id].append(spore)
            all_spores.append(spore)
            round_spores.append(spore)

        # Intra-round influence pass
        for spore in round_spores:
            x, y = spore["pos"]
            neighbors = []
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = (x + dx) % grid_size, (y + dy) % grid_size
                    neighbors.extend(grid.get((nx, ny), []))
            influence = _neighbor_influence(spore, neighbors)
            spore["resonance"] = round(
                spore["resonance"] * 0.7 + influence * 0.3, 3
            )

        round_log.append({
            "round": round_num,
            "spores": len(round_spores),
            "cells_used": len(set(s["pos"] for s in round_spores)),
        })

    # --- Emergent property analysis ---
    # 1. Type distribution
    type_counts = defaultdict(int)
    for s in all_spores:
        type_counts[s["type"]] += 1

    # 2. Spatial clustering: how many cells have >1 spore?
    occupied_cells = sum(1 for cells in grid.values() if cells)
    crowded_cells = sum(1 for cells in grid.values() if len(cells) > 1)
    max_density = max((len(cells) for cells in grid.values()), default=0)

    # 3. Resonance coherence: average |resonance| across all spores
    total_resonance = sum(abs(s["resonance"]) for s in all_spores)
    avg_resonance = total_resonance / len(all_spores) if all_spores else 0

    # 4. Unique fingerprints = production diversity
    fingerprints = set(s["fingerprint"] for s in all_spores)

    # 5. Constellation: what does the grid look like? (ASCII visualization)
    ascii_grid = [["." for _ in range(grid_size)] for _ in range(grid_size)]
    type_char = {"calcium": "C", "silk": "S", "prism": "P", "echo": "E", "void": "V"}
    for (x, y), cell_spores in grid.items():
        dominant = max(cell_spores, key=lambda s: s["weight"])
        ascii_grid[y][x] = type_char.get(dominant["type"], "?")

    # 6. Agent contribution analysis
    agent_stats = []
    for aid in range(agents):
        spores = agent_output[aid]
        types = defaultdict(int)
        for s in spores:
            types[s["type"]] += 1
        agent_stats.append({
            "agent": aid,
            "spores": len(spores),
            "dominant_type": max(types, key=types.get) if types else "?",
            "total_weight": round(sum(s["weight"] for s in spores), 3),
            "avg_resonance": round(
                sum(s["resonance"] for s in spores) / len(spores), 3
            ) if spores else 0,
        })

    return {
        "grid_size": grid_size,
        "agents": agents,
        "rounds": rounds,
        "total_spores": len(all_spores),
        "type_distribution": dict(type_counts),
        "spatial": {
            "occupied_cells": occupied_cells,
            "crowded_cells": crowded_cells,
            "max_density": max_density,
        },
        "emergence": {
            "resonance_coherence": round(avg_resonance, 4),
            "unique_fingerprints": len(fingerprints),
            "total_fingerprints": len(fingerprints),
            "pattern_diversity": round(len(fingerprints) / max(len(all_spores), 1), 4),
        },
        "ascii_constellation": [" ".join(row) for row in ascii_grid],
        "agent_contributions": agent_stats,
        "round_log": round_log,
        "philosophy": "Coral builds reefs. No single polyp designs the structure. Each contributes a spore. The reef emerges.",
    }


def main():
    ap = argparse.ArgumentParser(description="Sympoiesis simulation")
    ap.add_argument("--agents", type=int, default=12)
    ap.add_argument("--rounds", type=int, default=20)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--grid", type=int, default=20)
    args = ap.parse_args()
    result = simulate(args.agents, args.rounds, args.seed, args.grid)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
