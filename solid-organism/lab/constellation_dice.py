#!/usr/bin/env python3
"""Throw dice, place stars, and name the constellation they imply."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from typing import Any

GREEK = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta"]
ADJECTIVES = ["Quiet", "Branched", "Molten", "Patient", "Rebellious"]
NOUNS = ["Loom", "Threshold", "Orchard", "Signal", "Migration"]


def throw_dice(seed: int, stars: int = 5) -> dict[str, Any]:
    if not 3 <= stars <= len(GREEK):
        raise ValueError(f"stars must be between 3 and {len(GREEK)}")
    rng = random.Random(seed)
    points: set[tuple[int, int]] = set()
    while len(points) < stars:
        points.add((rng.randrange(9), rng.randrange(9)))
    ordered = [
        {"name": GREEK[index], "x": x, "y": y}
        for index, (x, y) in enumerate(sorted(points))
    ]
    edges = []
    for current, next_star in zip(ordered, ordered[1:]):
        distance = abs(current["x"] - next_star["x"]) + abs(current["y"] - next_star["y"])
        edges.append([current["name"], next_star["name"], distance])
    total = sum(edge[2] for edge in edges)
    title = f"The {ADJECTIVES[seed % len(ADJECTIVES)]} {NOUNS[(seed // 7 + total) % len(NOUNS)]}"
    myth = {
        "title": title,
        "seed": seed,
        "stars": ordered,
        "edges": edges,
        "span": total,
        "omen": "open" if total % 2 == 0 else "threshold",
        "signature": hashlib.sha256(json.dumps([ordered, edges], sort_keys=True).encode()).hexdigest()[:16],
    }
    return myth


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cast a deterministic constellation")
    parser.add_argument("--seed", type=int, default=616172)
    parser.add_argument("--stars", type=int, default=5)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(throw_dice(args.seed, args.stars), sort_keys=True, indent=2))
        return 0
    except ValueError as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
