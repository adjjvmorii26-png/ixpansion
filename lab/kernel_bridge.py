"""Kernel Bridge — Connects state_core, time_crystal, entanglement, paradox_solver.

Provides a unified kernel layer that manages global state, temporal
oscillations, quantum entanglement, and paradox resolution.
"""
from __future__ import annotations
import copy
import hashlib
import random
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class StateCore:
    def __init__(self, initial=None):
        self._state = initial or {}
        self._history: list[tuple[str, dict]] = []

    def get(self, path: str, default=None):
        keys = path.split(".")
        node = self._state
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return copy.deepcopy(node)

    def set(self, path: str, value):
        snapshot = copy.deepcopy(self._state)
        keys = path.split(".")
        node = self._state
        for key in keys[:-1]:
            node = node.setdefault(key, {})
        node[keys[-1]] = value
        h = hashlib.md5(str(snapshot).encode()).hexdigest()[:8]
        self._history.append((h, snapshot))

    def snapshot(self) -> dict:
        return copy.deepcopy(self._state)

    @property
    def history_length(self):
        return len(self._history)


class TimeCrystal:
    def __init__(self, period: int = 5, seed: int = 42):
        self.period = period
        self.tick_count = 0
        self.echoes: list[dict] = []
        self.rng = random.Random(seed)

    def pulse(self, agent_states: dict[str, dict]) -> dict:
        self.tick_count += 1
        phase = self.tick_count % self.period
        echo = None
        if phase == 0:
            echo = {
                "tick": self.tick_count,
                "agents": dict(agent_states),
                "type": "resonance",
            }
            self.echoes.append(echo)
        return {"tick": self.tick_count, "phase": phase, "echo": echo is not None}

    def get_echo(self, agent_id: str) -> dict | None:
        for echo in reversed(self.echoes):
            if agent_id in echo.get("agents", {}):
                return echo["agents"][agent_id]
        return None


class EntanglementManager:
    def __init__(self, seed=42):
        self.pairs: dict[tuple[str, str], float] = {}
        self.rng = random.Random(seed)

    def entangle(self, a: str, b: str, strength: float = 0.5):
        self.pairs[(a, b)] = strength
        self.pairs[(b, a)] = strength

    def correlate(self, a: str, b: str) -> float:
        return self.pairs.get((a, b), 0.0)

    def collapse(self, threshold: float = 0.8) -> list[tuple[str, str]]:
        collapsed = []
        for (a, b), strength in list(self.pairs.items()):
            if strength >= threshold:
                collapsed.append((a, b))
                del self.pairs[(a, b)]
                if (b, a) in self.pairs:
                    del self.pairs[(b, a)]
        return collapsed


class ParadoxSolver:
    def __init__(self):
        self.paradoxes: list[dict] = []
        self.resolutions: list[dict] = []

    def register(self, claim_a: str, claim_b: str, support_a: float, support_b: float):
        self.paradoxes.append({
            "claim_a": claim_a, "claim_b": claim_b,
            "support_a": support_a, "support_b": support_b,
        })

    def resolve(self) -> list[dict]:
        for p in self.paradoxes:
            if abs(p["support_a"] - p["support_b"]) < 0.1:
                strategy = "quantum_superposition"
                winner = f"both: {p['claim_a']} and {p['claim_b']}"
            elif p["support_a"] > p["support_b"]:
                strategy = "sacrifice_weaker"
                winner = p["claim_a"]
            else:
                strategy = "sacrifice_weaker"
                winner = p["claim_b"]
            resolution = {"strategy": strategy, "winner": winner, "paradox": p}
            self.resolutions.append(resolution)
        return self.resolutions


class KernelBridge:
    def __init__(self, seed=42):
        self.seed = seed
        self.state = StateCore({"epoch": 0, "agents": {}, "entropy": 0.0})
        self.crystal = TimeCrystal(period=5, seed=seed)
        self.entanglement = EntanglementManager(seed)
        self.paradox_solver = ParadoxSolver()
        self.tick_count = 0

    def tick(self) -> dict:
        self.tick_count += 1
        self.state.set("epoch", self.tick_count)
        agents = self.state.get("agents", {})
        crystal_result = self.crystal.pulse(agents)
        entropy = self.state.get("entropy", 0.0)
        self.state.set("entropy", entropy + random.Random(self.tick_count).uniform(-0.01, 0.02))
        return {
            "tick": self.tick_count,
            "crystal": crystal_result,
            "entropy": round(self.state.get("entropy", 0), 4),
        }

    def simulate(self, ticks: int = 10) -> dict:
        results = []
        for _ in range(ticks):
            results.append(self.tick())
        return {
            "ticks": ticks,
            "final_epoch": self.tick_count,
            "crystal_echoes": len(self.crystal.echoes),
            "state_history": self.state.history_length,
        }

    def report(self) -> dict:
        return {
            "bridge": "kernel_bridge",
            "ticks": self.tick_count,
            "state_snapshot": self.state.snapshot(),
            "crystal_period": self.crystal.period,
            "entangled_pairs": len(self.entanglement.pairs),
            "paradoxes_registered": len(self.paradox_solver.paradoxes),
        }


def demo():
    bridge = KernelBridge(seed=42)
    sim = bridge.simulate(ticks=15)
    bridge.entanglement.entangle("agent_a", "agent_b", 0.9)
    bridge.paradox_solver.register("growth is good", "growth is dangerous", 0.6, 0.7)
    resolutions = bridge.paradox_solver.resolve()
    return {"simulation": sim, "resolutions": resolutions, "report": bridge.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
