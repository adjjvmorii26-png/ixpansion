#!/usr/bin/env python3
"""Liminal Space: the threshold between states.

Liminality is the state of being "in-between" — not quite one thing, not
quite another. Corridors, doorways, dawn, dusk. This module analyzes a
dataset and finds the LIMINAL POINTS: values that sit at the boundary
between clusters, neither fully in one group nor another.

These edge-dwellers are often dismissed as outliers. But in complex systems,
the boundaries are where the interesting things happen — mutations, phase
transitions, innovation.

Usage:
    python3 liminal_space.py --seeds 25 --dimensions 3
    python3 liminal_space.py --anomaly

The `--anomaly` mode finds points that are liminal across ALL dimensions
simultaneously — the "veil-walkers" of the dataset.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from typing import Any, Dict, List, Tuple


def _distance(a: Tuple[float, ...], b: Tuple[float, ...]) -> float:
    """Euclidean distance."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _make_points(num_seeds: int, dims: int, seed: int) -> List[Tuple[float, ...]]:
    """Generate clustered points to analyze."""
    rng = random.Random(seed)
    points = []
    for _ in range(num_seeds):
        # random cluster center
        center = tuple(rng.uniform(-1, 1) for _ in range(dims))
        for _ in range(8):
            point = tuple(center[i] + rng.gauss(0, 0.15) for i in range(dims))
            points.append(point)
    return points


def _liminality_score(point: Tuple[float, ...], points: List[Tuple[float, ...]],
                      k: int = 8) -> Tuple[float, float, float]:
    """Compute how 'in-between' a point is.

    Returns (distance_to_nearest, local_membership_gap, liminality_score).
    A high liminality means the point is far from its own cluster
    but close to the boundary of another.
    """
    distances = sorted(_distance(point, p) for p in points if p != point)
    if not distances:
        return 0.0, 0.0, 0.0

    nearest = distances[0]
    kth_nearest = distances[min(k, len(distances) - 1)]
    average_neighbor = sum(distances[:k]) / min(k, len(distances))

    # Membership gap: how much farther is the kth neighbor than the nearest?
    membership_gap = (kth_nearest - nearest) / max(average_neighbor, 0.001)

    # Liminality: high when nearest is moderately far (not inside a cluster)
    # but the kth is not too far (still near SOMETHING)
    if nearest < 0.05:  # deep inside a cluster
        score = 0.0
    else:
        score = min(1.0, nearest * 3.0) * (1.0 - min(1.0, membership_gap * 0.5))

    return nearest, kth_nearest, max(0.0, score)


def analyze_points(points: List[Tuple[float, ...]], k: int = 8,
                   top_n: int = 10) -> Dict[str, Any]:
    """Analyze points and find the most liminal ones."""
    scored = []
    for i, point in enumerate(points):
        nearest, kth, lim = _liminality_score(point, points, k)
        scored.append({
            "index": i,
            "coords": [round(c, 4) for c in point],
            "nearest_dist": round(nearest, 4),
            "kth_nearest": round(kth, 4),
            "liminality": round(lim, 4),
        })

    scored.sort(key=lambda s: -s["liminality"])

    # Classification
    deep = [s for s in scored if s["nearest_dist"] < 0.05]
    liminal = [s for s in scored if s["nearest_dist"] >= 0.05 and s["liminality"] > 0.2]
    frontier = [s for s in scored if s["liminality"] > 0.45]  # veil-walkers

    return {
        "num_points": len(points),
        "distribution": {
            "deep_core": len(deep),
            "liminal_edge": len(liminal),
            "frontier": len(frontier),
        },
        "most_liminal": scored[:top_n],
        "frontier_points": [s for s in scored if s["liminality"] > 0.45][:5],
        "methodology": {
            "distance": "euclidean",
            "k_neighbors": k,
            "liminality_formula": "proximity * (1 - membership_gap_weighted)",
            "note": "Deep core = near one cluster. Liminal = between clusters. Frontier = the veil-walkers.",
        },
        "philosophy": (
            "The edges are where the interesting things happen. Mutations, "
            "phase transitions, innovation — none occur in the deep core. "
            "They occur in the liminal space, the threshold between states."
        ),
    }


def find_anomalies(points: List[Tuple[float, ...]], k: int = 8) -> Dict[str, Any]:
    """Find the most anomalous points (liminal across all dimensions)."""
    scored = []
    for i, point in enumerate(points):
        nearest, kth, lim = _liminality_score(point, points, k)
        # anomaly = nearest is large (isolated) but liminality is high
        anomaly = lim * (nearest / max(0.05, nearest))
        scored.append({"index": i, "coords": [round(c, 4) for c in point],
                       "nearest_dist": round(nearest, 4),
                       "liminality": round(lim, 4),
                       "anomaly_score": round(anomaly, 4)})

    scored.sort(key=lambda s: -s["anomaly_score"])
    return {
        "num_points": len(points),
        "anomalies": scored[:5],
        "top_anomaly": scored[0] if scored else None,
        "note": "Anomalies are liminal points that are ALSO isolated — they walk the veil alone.",
        "philosophy": "The lone wanderers carry the most information about the unknown.",
    }


def main():
    ap = argparse.ArgumentParser(description="Liminal Space analysis")
    ap.add_argument("--seeds", type=int, default=25, help="Number of cluster seeds")
    ap.add_argument("--dimensions", type=int, default=3)
    ap.add_argument("--anomaly", action="store_true", help="Anomaly detection mode")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    points = _make_points(args.seeds, args.dimensions, args.seed)

    if args.anomaly:
        result = find_anomalies(points)
    else:
        result = analyze_points(points)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
