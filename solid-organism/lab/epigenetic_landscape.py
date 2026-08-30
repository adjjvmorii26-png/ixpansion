#!/usr/bin/env python3
"""Epigenetic Landscape: cells rolling down Waddington's terrain.

Waddington's epigenetic landscape is a metaphor for cell differentiation:
a ball (cell) rolling down a landscape of valleys (fate choices). The deeper
the valley, the more irreversible the choice. This module generates a 2D
landscape, drops cells at the top, and watches them differentiate as they
roll down.

Usage:
    python3 epigenetic_landscape.py --cells 10 --depth 8 --seed 42
"""
from __future__ import annotations

import argparse
import json
import math
import random
from typing import Any, Dict, List, Tuple


def _landscape_function(x: float, y: float, depth: int) -> float:
    """Generate Waddington's landscape with branching valleys.

    The landscape has 5 distinct valleys that deepen as y increases.
    Cells roll downhill following the gradient, splitting at ridges.
    """
    h = 0.0
    # Base: gentle sinusoidal undulation
    for i in range(1, min(depth + 1, 4)):
        freq = 2.0 ** (i - 1)
        amp = 1.0 / (3.0 ** i)
        h += amp * math.sin(freq * x * math.pi * 2)
    
    # Main valleys: 5 parallel valleys that deepen with y
    num_valleys = 5
    for v in range(num_valleys):
        valley_x = (v + 0.5) / num_valleys
        valley_width = 0.06 + 0.02 * (y / 10.0)  # valleys widen slightly
        valley_depth = 1.5 * (y / 10.0)
        h += valley_depth * math.exp(-((x - valley_x) ** 2) / (2 * valley_width ** 2))
    
    # Ridge separators (subtle) between valleys
    for v in range(1, num_valleys):
        ridge_x = v / num_valleys
        ridge_height = 0.3 * (y / 10.0)
        h -= ridge_height * math.exp(-((x - ridge_x) ** 2) * 200)
    
    return h


def simulate(num_cells: int = 10, landscape_depth: int = 6,
             num_steps: int = 100, seed: int = 42) -> Dict[str, Any]:
    """Simulate cells rolling down Waddington's landscape."""
    rng = random.Random(seed)
    
    # Initialize cells at the top (y=0) spread across x
    cells = []
    for _ in range(num_cells):
        x = rng.uniform(0.1, 0.9)
        cells.append({
            "x": x,
            "y": 0.0,
            "vx": 0.0,
            "vy": 0.0,
            "path": [{"x": x, "y": 0.0}],
            "fate": None,
        })
    
    # Valleys at these x positions
    valleys = [0.1, 0.3, 0.5, 0.7, 0.9]
    fate_names = ["neuron", "muscle", "blood", "skin", "bone"]
    fate_count = {}
    
    for step in range(num_steps):
        for cell in cells:
            if cell["fate"]:
                continue
            
            # Gravity pulls cells DOWN (increasing y)
            gravity = 0.12
            
            # Horizontal force: nearest valley pulls the cell toward it
            nearest_valley = min(valleys, key=lambda v: abs(cell["x"] - v))
            pull = (nearest_valley - cell["x"]) * 0.5
            
            # Add noise for stochasticity
            cell["vx"] = pull + rng.gauss(0, 0.01)
            cell["vy"] = gravity + rng.gauss(0, 0.005)
            
            # Update position
            cell["x"] += cell["vx"]
            cell["y"] += cell["vy"]
            
            # Clamp x to [0, 1]
            cell["x"] = max(0.01, min(0.99, cell["x"]))
            
            cell["path"].append({"x": round(cell["x"], 4), "y": round(cell["y"], 4)})
            
            # Cell has differentiated when it's deep in a valley (y > 8)
            if cell["y"] > 8.0:
                # Find which valley it landed in
                nearest_idx = min(range(len(valleys)), key=lambda i: abs(cell["x"] - valleys[i]))
                cell["fate"] = fate_names[nearest_idx]
                fate_count[cell["fate"]] = fate_count.get(cell["fate"], 0) + 1
    
    # Analysis
    final_positions = [{"x": round(c["x"], 3), "y": round(c["y"], 3), 
                        "fate": c["fate"] or "undifferentiated"} for c in cells]
    
    # Count fates
    differentiated = [c for c in cells if c["fate"]]
    undifferentiated = [c for c in cells if not c["fate"]]
    
    # Generate landscape visualization (ASCII)
    ascii_landscape = []
    for row in range(0, 10, 1):
        line = ""
        for col in range(20):
            x_pos = col / 19.0
            h = _landscape_function(x_pos, row, landscape_depth)
            chars = " .:-=+*#%@"
            idx = int((h + 1) * (len(chars) - 1) / 3)
            idx = max(0, min(len(chars) - 1, idx))
            line += chars[idx]
        ascii_landscape.append(line)
    
    return {
        "num_cells": num_cells,
        "landscape_depth": landscape_depth,
        "num_steps": num_steps,
        "differentiated": len(differentiated),
        "undifferentiated": len(undifferentiated),
        "fate_distribution": fate_count,
        "final_positions": final_positions,
        "ascii_landscape": ascii_landscape,
        "philosophy": (
            "A stem cell rolls down Waddington's landscape. At each valley fork, "
            "it commits deeper. The deeper the valley, the harder the return. "
            "This is differentiation: the irreversible choice of what to become."
        ),
    }


def main():
    ap = argparse.ArgumentParser(description="Epigenetic Landscape simulation")
    ap.add_argument("--cells", type=int, default=10)
    ap.add_argument("--depth", type=int, default=6)
    ap.add_argument("--steps", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    result = simulate(args.cells, args.depth, args.steps, args.seed)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
