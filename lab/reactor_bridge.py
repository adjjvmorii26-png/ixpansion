"""Reactor Bridge — Connects chaos, order, fusion, and inversion reactors.

Provides a unified reactor system that can apply multiple transformations
to state simultaneously, creating complex emergent behaviors.
"""
from __future__ import annotations
import random
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class ChaosReactor:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.injections = 0

    def inject(self, state: dict, magnitude: float = 0.1) -> dict:
        for key, value in list(state.items()):
            if isinstance(value, (int, float)) and not key.startswith("_"):
                noise = self.rng.gauss(0, magnitude * abs(value) if value else magnitude)
                state[key] = round(value + noise, 6)
                self.injections += 1
        return state


class OrderReactor:
    def __init__(self):
        self.organizations = 0

    def organize(self, state: dict) -> dict:
        for key, value in list(state.items()):
            if isinstance(value, float):
                state[key] = round(value, 2)
                self.organizations += 1
            elif isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                state[key] = sorted(value)
                self.organizations += 1
        return state


class FusionReactor:
    def __init__(self):
        self.fusions = 0

    def fuse(self, state_a: dict, state_b: dict) -> dict:
        result = {}
        all_keys = set(state_a.keys()) | set(state_b.keys())
        for key in all_keys:
            va = state_a.get(key)
            vb = state_b.get(key)
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                result[key] = (va + vb) / 2
            elif va is not None:
                result[key] = va
            elif vb is not None:
                result[key] = vb
        self.fusions += 1
        return result


class InversionReactor:
    def __init__(self):
        self.inversions = 0

    def invert(self, state: dict) -> dict:
        result = {}
        for key, value in state.items():
            if isinstance(value, (int, float)):
                result[key] = -value
            elif isinstance(value, bool):
                result[key] = not value
            elif isinstance(value, str):
                result[key] = value[::-1]
            else:
                result[key] = value
        self.inversions += 1
        return result


class ReactorBridge:
    def __init__(self, seed=42):
        self.seed = seed
        self.chaos = ChaosReactor(seed)
        self.order = OrderReactor()
        self.fusion = FusionReactor()
        self.inversion = InversionReactor()
        self.log: list[dict] = []

    def apply_pipeline(self, state: dict, steps: list[str]) -> dict:
        current = dict(state)
        for step in steps:
            if step == "chaos":
                current = self.chaos.inject(current, magnitude=0.05)
            elif step == "order":
                current = self.order.organize(current)
            elif step == "invert":
                current = self.inversion.invert(current)
            self.log.append({"step": step, "state_hash": hash(str(current)) % 10000})
        return current

    def full_cycle(self, state: dict) -> dict:
        chaos_out = self.chaos.inject(dict(state), magnitude=0.05)
        order_out = self.order.organize(dict(state))
        fused = self.fusion.fuse(chaos_out, order_out)
        inverted = self.inversion.invert(dict(fused))
        final = self.fusion.fuse(fused, inverted)
        return final

    def report(self) -> dict:
        return {
            "bridge": "reactor_bridge",
            "chaos_injections": self.chaos.injections,
            "order_organizations": self.order.organizations,
            "fusion_count": self.fusion.fusions,
            "inversion_count": self.inversion.inversions,
            "pipeline_steps": len(self.log),
        }


def demo():
    bridge = ReactorBridge(seed=42)
    state = {"energy": 0.85, "entropy": 0.32, "complexity": 0.67, "cohesion": 0.91, "epoch": 5}
    pipeline_result = bridge.apply_pipeline(state, ["chaos", "order", "invert", "chaos", "order"])
    cycle_result = bridge.full_cycle(state)
    return {"pipeline": pipeline_result, "cycle": cycle_result, "report": bridge.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
