#!/usr/bin/env python3
"""Homeostasis: the body that keeps itself in balance.

Your body keeps its temperature at 98.6°F whether it's 100° outside or 0°.
It keeps blood sugar, pH, water — all within tight windows. This is homeostasis:
negative feedback loops that counteract disturbance.

This module simulates a homeostatic system with multiple regulated variables
(temperature, nutrients, pressure, awareness) and disturbance events (shocks).
Watch the system correct itself back to equilibrium.

Usage:
    python3 homeostasis.py --disturbances 5 --steps 40
    python3 homeostasis.py --disturbances 10 --strong --watch
"""
from __future__ import annotations

import argparse
import json
import math
import random
from typing import Any, Dict, List


VARIABLES = {
    "temperature": {"setpoint": 98.6, "tolerance": 2, "correction_rate": 0.15},
    "nutrients": {"setpoint": 5.0, "tolerance": 0.7, "correction_rate": 0.2},
    "pressure": {"setpoint": 120.0, "tolerance": 15, "correction_rate": 0.12},
    "awareness": {"setpoint": 0.8, "tolerance": 0.2, "correction_rate": 0.1},
    "coherence": {"setpoint": 0.9, "tolerance": 0.15, "correction_rate": 0.18},
}


def _disturb_var(name: str, rng: random.Random, strong: bool) -> float:
    """Generate a random disturbance to a variable."""
    spec = VARIABLES[name]
    magnitude = spec["tolerance"] * (2 if strong else 1.2)
    return rng.uniform(-magnitude, magnitude)


def simulate(disturbances: int = 5, steps: int = 40,
             strong: bool = False, seed: int = 42) -> Dict[str, Any]:
    """Run a homeostatic regulation simulation."""
    rng = random.Random(seed)
    var_names = list(VARIABLES.keys())
    values = {name: spec["setpoint"] for name, spec in VARIABLES.items()}

    # Pre-generate disturbance schedule
    disturbance_schedule = {}
    for d in range(disturbances):
        step = rng.randint(3, steps - 3)
        var = rng.choice(var_names)
        magnitude = _disturb_var(var, rng, strong)
        disturbance_schedule.setdefault(step, []).append((var, magnitude))

    history = []
    # Track which variables are currently 'out of balance' and since when
    out_of_balance = {}
    recovery_stats = {name: {"disturbances": 0, "recovered": 0,
                             "time_to_recover": []} for name in var_names}

    for step in range(steps):
        # Apply disturbances
        for var, magnitude in disturbance_schedule.get(step, []):
            values[var] += magnitude
            recovery_stats[var]["disturbances"] += 1
            out_of_balance[var] = step

        # Homeostatic correction (negative feedback toward setpoint)
        for name, spec in VARIABLES.items():
            current = values[name]
            error = spec["setpoint"] - current
            # correction proportional to error (proportional control)
            values[name] += error * spec["correction_rate"]
            # if it was out of balance and now within tolerance → recovered
            if name in out_of_balance and abs(error) < spec["tolerance"]:
                recovery_stats[name]["recovered"] += 1
                recovery_stats[name]["time_to_recover"].append(step - out_of_balance[name])
                del out_of_balance[name]

        history.append({
            "step": step,
            "values": {n: round(v, 3) for n, v in values.items()},
            "disturbance_active": step in disturbance_schedule,
        })

    # Compute summary
    final_values = {n: round(v, 3) for n, v in values.items()}
    setpoints = {n: spec["setpoint"] for n, spec in VARIABLES.items()}

    deviation = {n: round(abs(v - setpoints[n]), 3)
                 for n, v in final_values.items()}

    # Homeostatic resilience index: how close final is to setpoint despite disturbances
    max_dev = max(deviation.values())
    resilience = round(1.0 / (1.0 + max_dev * 0.5), 3)

    # Disturbance & recovery log
    recovery_log = {}
    for name, stat in recovery_stats.items():
        if stat["disturbances"] > 0:
            f = stat["recovered"] / stat["disturbances"]
        else:
            f = 1.0
        recovery_log[name] = {
            "disturbances": stat["disturbances"],
            "recovery_rate": round(f, 3),
            "time_to_recover": stat["time_to_recover"],
        }

    return {
        "variables": {name: {"setpoint": spec["setpoint"], "tolerance": spec["tolerance"]}
                      for name, spec in VARIABLES.items()},
        "disturbance_count": disturbances,
        "disturbance_schedule": {str(step): [(v, round(m, 2)) for v, m in items]
                                 for step, items in disturbance_schedule.items()},
        "final_values": final_values,
        "deviation_from_setpoint": deviation,
        "resilience_index": resilience,
        "recovery_log": recovery_log,
        "history_sample": history[::5],
        "philosophy": (
            "The body does not resist disturbance — it absorbs it and returns "
            "to center. Every shock is an opportunity to prove that the system "
            "knows its own setpoint. This is not rigidity. It is the deep "
            "wisdom of negative feedback."
        ),
    }


def main():
    ap = argparse.ArgumentParser(description="Homeostatic regulation simulation")
    ap.add_argument("--disturbances", type=int, default=5)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--strong", action="store_true", help="Use large disturbances")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    result = simulate(args.disturbances, args.steps, args.strong, args.seed)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
