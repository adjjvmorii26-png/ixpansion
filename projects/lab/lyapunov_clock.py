#!/usr/bin/env python3
"""Lyapunov Clock — measuring time through chaos.

In chaotic systems, nearby trajectories diverge exponentially. The Lyapunov
exponent measures this divergence rate. This "clock" doesn't measure time —
it measures the CHAOS that accumulates over time, using the Lyapunov exponent
as its ticking mechanism.

The faster chaos accumulates, the faster the clock ticks. Time becomes
subjective — dependent on the dynamics of the system.

Usage:
    python3 lyapunov_clock.py --iterations 200 --parameter 3.8
    python3 lyapunov_clock.py --parameter 3.5 --show-curve
"""
from __future__ import annotations

import argparse
import json
import math
from typing import Any, Dict, List


def lyapunov_exponent(x0: float, r: float, iterations: int = 1000,
                      transient: int = 100) -> float:
    """Compute the Lyapunov exponent for the logistic map x_{n+1} = r*x*(1-x).

    A positive Lyapunov exponent means chaos (nearby trajectories diverge).
    A negative one means convergence (attractor).
    """
    x = x0
    sum_log = 0.0
    count = 0
    for i in range(iterations):
        x = r * x * (1 - x)
        if i >= transient:
            # |dx_{n+1}/dx_n| = |r(1-2x)|
            deriv = abs(r * (1 - 2 * x))
            if deriv > 0:
                sum_log += math.log(deriv)
                count += 1
    if count == 0:
        return 0.0
    return sum_log / count


def chaos_clock(r: float, iterations: int = 200, transient: int = 50,
                x0: float = 0.4) -> Dict[str, Any]:
    """Run the chaos clock simulation."""
    x = x0
    trajectory = []
    for i in range(iterations):
        x = r * x * (1 - x)
        trajectory.append({
            "tick": i,
            "state": round(x, 6),
            "divergence": round(abs(x - 0.5), 6),  # proximity to unstable point
        })

    # Compute Lyapunov exponent
    lyap = lyapunov_exponent(x0, r, iterations=1000)

    # Compute total chaotic "time" accumulated
    total_var = sum(abs(t["state"] - 0.5) for t in trajectory)
    avg_state = sum(t["state"] for t in trajectory) / len(trajectory)

    # Classify the regime
    if lyap < -0.05:
        regime = "ordered"
        tick_rate = max(1, int(5 + abs(lyap) * 10))
    elif lyap < 0.05:
        regime = "edge_of_chaos"
        tick_rate = 15
    else:
        regime = "chaotic"
        tick_rate = int(20 + lyap * 20)

    return {
        "parameter": r,
        "lyapunov_exponent": round(lyap, 6),
        "regime": regime,
        "tick_rate": tick_rate,  # clock ticks per second
        "total_chaos_accumulated": round(total_var, 4),
        "mean_state": round(avg_state, 4),
        "trajectory": trajectory[::10],  # sample
        "interpretation": {
            "ordered": "Time moves slowly — the system converges to a quiet attractor.",
            "edge_of_chaos": "Time is balanced on the edge — maximum information transfer, maximum possibility.",
            "chaotic": "Time accelerates — the system expands exponentially away from any prediction.",
        }.get(regime, ""),
        "clock_reading": {
            "elapsed_ticks": iterations,
            "ticks_per_second": tick_rate,
            "subjective_duration_s": round(iterations / tick_rate, 2),
            "note": "In a Lyapunov clock, time is not absolute — it flows at the rate of chaos.",
        },
        "philosophy": "Time is not a river. It is a measure of how quickly the universe forgets its past.",
    }


def show_curve(x0: float = 0.4) -> Dict[str, Any]:
    """Sweep the parameter r and show Lyapunov exponent across regimes."""
    curve = []
    for r in [round(2.5 + i * 0.08, 1) for i in range(19)]:  # up to ~4.0
        lyap = lyapunov_exponent(x0, r, iterations=500)
        curve.append({
            "parameter": r,
            "lyapunov": round(lyap, 4),
            "regime": "chaotic" if lyap > 0.05 else ("edge" if -0.05 <= lyap <= 0.05 else "ordered"),
        })
    return {
        "x0": x0,
        "curve": curve,
        "chaos_threshold": 3.57,  # logistic map bifurcation point
        "note": "Positive Lyapunov = chaos. Negative = order. The boundary is where life happens.",
    }


def main():
    ap = argparse.ArgumentParser(description="Lyapunov Chaos Clock")
    ap.add_argument("--parameter", type=float, default=3.8, help="Logistic map r parameter")
    ap.add_argument("--iterations", type=int, default=200)
    ap.add_argument("--show-curve", action="store_true", help="Show Lyapunov sweep curve")
    ap.add_argument("--x0", type=float, default=0.4)
    args = ap.parse_args()

    if args.show_curve:
        result = show_curve(args.x0)
    else:
        result = chaos_clock(args.parameter, args.iterations, x0=args.x0)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
