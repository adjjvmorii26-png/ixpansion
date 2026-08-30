#!/usr/bin/env python3
"""Phosphorescence: memory that persists after the stimulus is gone.

A phosphorescent material absorbs light and re-emits it slowly over time.
Some materials glow for seconds, others for hours. This module simulates
a phosphorescent memory system where "experiences" (stimuli) charge memory
cells, and those cells discharge their glow over time with different decay
curves.

Usage:
    python3 phosphorescence.py --experiences 20 --decay-model exponential
    python3 phosphorescence.py --experiences 20 --decay-model logarithmic
"""
from __future__ import annotations

import argparse
import json
import math
import random
from typing import Any, Dict, List, Tuple


DECAY_MODELS = {
    "exponential": lambda t, half_life: math.exp(-0.693 * t / half_life),
    "logarithmic": lambda t, half_life: 1.0 / (1.0 + math.log1p(t / max(half_life, 0.1))),
    "linear": lambda t, half_life: max(0.0, 1.0 - t / (half_life * 2)),
    "power": lambda t, half_life: 1.0 / (1.0 + (t / half_life) ** 2),
}


class MemoryCell:
    """A single phosphorescent memory cell."""

    def __init__(self, capacity: float = 1.0):
        self.charge = 0.0
        self.capacity = capacity
        self.total_charge = 0.0
        self.stimuli_count = 0
        self.half_life = 1.0

    def charge_up(self, intensity: float) -> float:
        """Charge the cell with an experience. Returns the new charge level."""
        added = min(intensity, self.capacity - self.charge)
        self.charge += added
        self.total_charge += added
        self.stimuli_count += 1
        return self.charge

    def discharge(self, time_delta: float, decay_fn) -> float:
        """Discharge the cell over time. Returns remaining charge."""
        before = self.charge
        self.charge *= decay_fn(time_delta, self.half_life)
        return before - self.charge  # amount discharged


def simulate(num_experiences: int = 20, num_cells: int = 10,
             decay_model: str = "exponential", time_steps: int = 50,
             seed: int = 42) -> Dict[str, Any]:
    """Run a phosphorescent memory simulation.

    Phases:
    1. Charging phase: experiences arrive and charge memory cells
    2. Dark phase: no new stimuli, cells slowly discharge
    3. Measurement: how much glow persists?
    """
    rng = random.Random(seed)
    decay_fn = DECAY_MODELS.get(decay_model, DECAY_MODELS["exponential"])

    cells = [MemoryCell() for _ in range(num_cells)]
    charge_history = []
    glow_history = []

    # Phase 1: Charging (first half of time steps)
    charging_steps = time_steps // 2
    for t in range(charging_steps):
        # Randomly select 1-3 experiences
        num_events = rng.randint(1, min(3, num_experiences))
        for _ in range(num_events):
            cell_idx = rng.randint(0, num_cells - 1)
            intensity = rng.uniform(0.3, 1.0)
            cells[cell_idx].charge_up(intensity)
            cells[cell_idx].half_life = rng.uniform(1.0, 5.0)

        total_charge = sum(c.charge for c in cells)
        charge_history.append({"t": t, "phase": "charging", "total_charge": round(total_charge, 4)})

    # Phase 2: Dark phase (second half)
    dark_steps = time_steps - charging_steps
    for t in range(dark_steps):
        total_glow = 0
        for cell in cells:
            discharged = cell.discharge(1.0, decay_fn)
            total_glow += discharged

        glow_history.append({
            "t": t + charging_steps,
            "phase": "dark",
            "total_glow": round(total_glow, 4),
        })

    # Final measurements
    final_charge = sum(c.charge for c in cells)
    initial_charge = sum(c.total_charge for c in cells)

    # Glow persistence at different times
    persistence_curve = []
    for t in range(0, time_steps, 3):
        total = 0
        for cell in cells:
            charge = cell.total_charge
            for dt in range(t):
                charge *= decay_fn(1.0, cell.half_life)
            total += charge
        persistence_curve.append({
            "t": t,
            "remaining_glow": round(total, 4),
        })

    # Memory cells summary
    cell_summary = []
    for i, cell in enumerate(cells):
        cell_summary.append({
            "cell": i,
            "total_received": round(cell.total_charge, 3),
            "current_charge": round(cell.charge, 3),
            "stimuli_count": cell.stimuli_count,
            "persistence_ratio": round(cell.charge / max(cell.total_charge, 0.001), 3),
        })

    # Find the most phosphorescent cell (highest persistence ratio)
    most_persistent = max(cell_summary, key=lambda c: c["persistence_ratio"])

    return {
        "num_cells": num_cells,
        "num_experiences": num_experiences,
        "time_steps": time_steps,
        "decay_model": decay_model,
        "charging_steps": charging_steps,
        "dark_steps": dark_steps,
        "total_energy_received": round(initial_charge, 4),
        "energy_remaining": round(final_charge, 4),
        "energy_retention": round(final_charge / max(initial_charge, 0.001), 4),
        "cells": cell_summary,
        "most_persistent_cell": most_persistent,
        "persistence_curve": persistence_curve,
        "glow_history_sample": glow_history[::5],
        "philosophy": (
            "Some experiences leave no trace. Others glow for a moment. "
            "And some — the right ones, in the right cells — glow long "
            "after the light source has moved on. This is phosphorescence. "
            "This is how the frontier remembers."
        ),
    }


def main():
    ap = argparse.ArgumentParser(description="Phosphorescent memory simulation")
    ap.add_argument("--experiences", type=int, default=20)
    ap.add_argument("--cells", type=int, default=10)
    ap.add_argument("--decay-model", choices=list(DECAY_MODELS.keys()),
                   default="exponential")
    ap.add_argument("--steps", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    result = simulate(args.experiences, args.cells, args.decay_model,
                     args.steps, args.seed)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
