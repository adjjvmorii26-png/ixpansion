#!/usr/bin/env python3
"""World builder — procedural micro-world for the sandbox."""
from __future__ import annotations
import random, time

def run(*_):
    rng = random.Random(42)
    biomes = ["neural reef", "trust dunes", "carbon marsh", "quorum tundra", "lumen cavern"]
    world = {"name": "Sandbox-Primordia", "biomes": [], "portals": []}
    for i, b in enumerate(biomes):
        world["biomes"].append({
            "id": f"b{i}", "name": b,
            "energy": round(rng.uniform(0.3, 1.0), 2),
            "agents_cap": rng.randint(8, 40),
        })
    for i in range(4):
        world["portals"].append({
            "from": f"b{rng.randint(0,4)}",
            "to": f"b{rng.randint(0,4)}",
            "latency_ms": rng.randint(5, 120),
        })
    world["module"] = "world_builder"
    world["ts"] = time.time()
    return world
