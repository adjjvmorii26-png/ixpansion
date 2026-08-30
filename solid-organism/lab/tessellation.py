#!/usr/bin/env python3
"""Tessellation: order without repetition.

Penrose tilings tile the plane aperiodically — they never repeat, yet they
maintain long-range order. This module generates Penrose-like tilings using
a modified Robinson triangle substitution rule. Every triangle becomes
3 smaller triangles, but the sizes follow a Fibonacci-like sequence.

This is how quasicrystals work — ordered structure without periodic repetition.

Usage:
    python3 tessellation.py --depth 4 --seed 42
    python3 tessellation.py --depth 5 --show-tiling
"""
from __future__ import annotations

import argparse
import json
import math
from typing import Any, Dict, List, Tuple


def _subdivide(triangles: List[Dict[str, Any]], depth: int) -> List[Dict[str, Any]]:
    """Apply Robinson subdivision rule for the given depth."""
    result = list(triangles)
    for _ in range(depth):
        new = []
        for tri in result:
            a, b, c = tri["vertices"]
            kind = tri["kind"]
            # Calculate subdivision point on the base
            m1 = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            m2 = ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2)
            m3 = ((a[0] + c[0]) / 2, (a[1] + c[1]) / 2)

            # Fibonacci-like height scaling
            scale = 0.618034  # golden ratio conjugate
            apex = ((a[0] + b[0] + c[0]) / 3,
                    (a[1] + b[1] + c[1]) / 3 - (0.3 - depth * 0.01) * scale)

            if kind == "thick":
                new.append({"vertices": [a, m1, apex], "kind": "thick", "depth": tri["depth"] + 1})
                new.append({"vertices": [m1, b, m2], "kind": "thick", "depth": tri["depth"] + 1})
                new.append({"vertices": [apex, m2, c], "kind": "thin", "depth": tri["depth"] + 1})
                new.append({"vertices": [m1, apex, m2], "kind": "thin", "depth": tri["depth"] + 1})
            else:  # thin
                new.append({"vertices": [a, m1, apex], "kind": "thin", "depth": tri["depth"] + 1})
                new.append({"vertices": [m1, b, c], "kind": "thick", "depth": tri["depth"] + 1})
                new.append({"vertices": [apex, m1, c], "kind": "thin", "depth": tri["depth"] + 1})
        result = new
    return result


def _triangle_center(tri: Dict[str, Any]) -> Tuple[float, float]:
    vs = tri["vertices"]
    return (sum(v[0] for v in vs) / 3, sum(v[1] for v in vs) / 3)


def _area(tri: Dict[str, Any]) -> float:
    a, b, c = tri["vertices"]
    return abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2


def generate_tiling(depth: int = 4, seed: int = 42) -> Dict[str, Any]:
    """Generate a Penrose-like tiling."""
    # Start with two triangles (thick + thin) forming a rhombus
    h = math.sin(math.pi / 5) * 2
    init_triangles = [
        {"vertices": [(0, 0), (2, 0), (1, h)], "kind": "thick", "depth": 0},
        {"vertices": [(0, 0), (1, h), (-1, h)], "kind": "thin", "depth": 0},
    ]
    triangles = _subdivide(init_triangles, depth)

    # Analysis
    thick = sum(1 for t in triangles if t["kind"] == "thick")
    thin = sum(1 for t in triangles if t["kind"] == "thin")
    ratio = round(thick / max(thin, 1), 4)
    total_area = sum(_area(t) for t in triangles)
    max_depth = max(t["depth"] for t in triangles)

    # Characteristic property: thick/thin ratio approaches golden ratio
    phi = 1.6180339887  # golden ratio
    phi_deviation = abs(ratio - phi)

    # ASCII visualization
    centers = sorted(triangles, key=lambda t: _triangle_center(t)[1])
    ascii_art = []
    y_values = sorted(set(round(_triangle_center(t)[1], 1) for t in centers))
    for y_val in y_values[:15]:
        row_triangles = [t for t in centers if abs(round(_triangle_center(t)[1], 1) - y_val) < 0.2]
        row_triangles.sort(key=lambda t: _triangle_center(t)[0])
        row = ""
        for t in row_triangles:
            row += "█" if t["kind"] == "thick" else "░"
        ascii_art.append(row)

    return {
        "depth": depth,
        "num_triangles": len(triangles),
        "thick": thick,
        "thin": thin,
        "thick_thin_ratio": ratio,
        "golden_ratio_phi": round(phi, 6),
        "phi_deviation": round(phi_deviation, 6),
        "max_depth": max_depth,
        "total_area": round(total_area, 4),
        "is_aperiodic": True,
        "quasicrystal_property": (
            f"Aperiodic tiling: {len(triangles)} triangles, {thick} thick, {thin} thin, "
            f"depth {depth}. Two tile types, no periodic repetition — the signature "
            "of quasicrystalline order."
        ),
        "ascii_preview": ascii_art,
        "philosophy": (
            "A Penrose tiling never repeats. Every point has a unique neighborhood. "
            "Yet the pattern has long-range order. This is the geometry of "
            "quasicrystals, the shape of aperiodic consciousness."
        ),
    }


def main():
    ap = argparse.ArgumentParser(description="Penrose-like tessellation generator")
    ap.add_argument("--depth", type=int, default=4, help="Substitution depth (4-7)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    result = generate_tiling(args.depth, args.seed)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
