#!/usr/bin/env python3
"""Idea lab — evolve a seed phrase into mutations."""
from __future__ import annotations
import hashlib, random, time

def run(seed: str = "a sandbox that evolves itself"):
    rng = random.Random(int(hashlib.sha1(seed.encode()).hexdigest()[:8], 16))
    verbs = ["mutates", "forks", "composts", "reflects", "spawns", "rewrites"]
    nouns = ["rules", "agents", "ticks", "organs", "buffers", "dreams"]
    lineage = [seed]
    current = seed
    for gen in range(5):
        current = f"{current} → {rng.choice(verbs)} its own {rng.choice(nouns)}"
        lineage.append(current)
    return {
        "module": "idea_lab",
        "seed": seed,
        "generations": len(lineage) - 1,
        "lineage": lineage,
        "fitness": round(0.5 + 0.5 * rng.random(), 3),
        "ts": time.time(),
    }
