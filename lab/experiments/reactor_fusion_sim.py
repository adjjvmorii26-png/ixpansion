#!/usr/bin/env python3
"""Reactor Fusion Simulator — pipeline of chaos, order, fusion, and inversion.

Bridges all four omega_fractal_engine reactors into a single simulation
pipeline. A system state passes through reactors in sequence:
1. Chaos injects randomness
2. Order snaps values toward structure
3. Fusion blends two states
4. Inversion flips everything

The simulator tracks how each reactor transforms the state and measures
the "entropy budget" consumed at each stage. This reveals the cost
of each transformation type.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StateSnapshot:
    tick: int
    state: dict[str, Any]
    entropy_cost: float
    reactor_used: str

    def payload(self) -> dict[str, Any]:
        return {
            "tick": self.tick,
            "state": {k: round(v, 4) if isinstance(v, float) else v
                      for k, v in self.state.items()},
            "entropy_cost": round(self.entropy_cost, 4),
            "reactor": self.reactor_used,
        }


@dataclass
class ReactorFusionSimulator:
    """Pipeline of reactors transforming system state."""
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._timeline: list[StateSnapshot] = []
        self._tick = 0

    def run_pipeline(self, initial_state: dict[str, Any],
                     reactors: list[str], steps: int = 5) -> dict[str, Any]:
        """Run a sequence of reactors over multiple steps."""
        state = dict(initial_state)
        total_cost = 0.0

        for step in range(steps):
            for reactor_name in reactors:
                self._tick += 1
                cost = 0.0

                if reactor_name == "chaos":
                    state, cost = self._apply_chaos(state)
                elif reactor_name == "order":
                    state, cost = self._apply_order(state)
                elif reactor_name == "fusion":
                    state, cost = self._apply_fusion(state)
                elif reactor_name == "inversion":
                    state, cost = self._apply_inversion(state)

                total_cost += cost
                self._timeline.append(StateSnapshot(
                    tick=self._tick, state=dict(state),
                    entropy_cost=cost, reactor_used=reactor_name,
                ))

        signature = hashlib.sha256(
            json.dumps([s.payload() for s in self._timeline[-3:]],
                       sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()[:16]

        return {
            "steps": len(self._timeline),
            "total_entropy_cost": round(total_cost, 4),
            "final_state": self._timeline[-1].payload() if self._timeline else {},
            "pipeline_signature": signature,
            "timeline": [s.payload() for s in self._timeline],
        }

    def _apply_chaos(self, state: dict[str, Any]) -> tuple[dict[str, Any], float]:
        cost = 0.0
        for key, val in state.items():
            if isinstance(val, (int, float)) and not key.startswith("_"):
                noise = self._rng.gauss(0, 0.1 * abs(val) if val else 0.1)
                state[key] = val + noise
                cost += abs(noise)
        return state, cost

    def _apply_order(self, state: dict[str, Any]) -> tuple[dict[str, Any], float]:
        cost = 0.0
        for key, val in state.items():
            if isinstance(val, float):
                snapped = round(val * 4) / 4
                if abs(val - snapped) < 0.1:
                    cost += abs(val - snapped)
                    state[key] = snapped
        return state, cost

    def _apply_fusion(self, state: dict[str, Any]) -> tuple[dict[str, Any], float]:
        cost = 0.0
        keys = list(state.keys())
        for i in range(0, len(keys) - 1, 2):
            k1, k2 = keys[i], keys[i + 1]
            if isinstance(state[k1], (int, float)) and isinstance(state[k2], (int, float)):
                blend = (state[k1] + state[k2]) / 2
                cost += abs(state[k1] - state[k2]) * 0.5
                state[k1] = blend
                state[k2] = blend
        return state, cost

    def _apply_inversion(self, state: dict[str, Any]) -> tuple[dict[str, Any], float]:
        cost = 0.0
        for key, val in state.items():
            if isinstance(val, bool):
                state[key] = not val
                cost += 0.1
            elif isinstance(val, (int, float)):
                state[key] = -val
                cost += abs(val)
            elif isinstance(val, str):
                state[key] = val[::-1]
                cost += 0.05
        return state, cost


def demo() -> dict[str, Any]:
    sim = ReactorFusionSimulator(seed=42)
    initial = {"energy": 0.8, "entropy": 0.3, "coherence": 0.6, "signal": 0.5, "chaos_level": 0.2}
    return sim.run_pipeline(initial, reactors=["chaos", "order", "fusion", "inversion"], steps=3)


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
