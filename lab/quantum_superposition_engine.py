"""Quantum Superposition Engine — Holds multiple states simultaneously.

Modules exist in superposition until measured. The engine computes
all possible outcomes and finds the most probable configuration.
"""
from __future__ import annotations
import hashlib
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class QuantumState:
    def __init__(self, basis: list[str], seed=42):
        self.rng = random.Random(seed)
        self.amplitudes: dict[str, complex] = {}
        total = 0.0
        for b in basis:
            amp = complex(self.rng.uniform(-1, 1), self.rng.uniform(-1, 1))
            self.amplitudes[b] = amp
            total += abs(amp) ** 2
        for b in self.amplitudes:
            self.amplitudes[b] /= math.sqrt(total)

    def probability(self, basis: str) -> float:
        return abs(self.amplitudes.get(basis, 0)) ** 2

    def measure(self) -> str:
        r = self.rng.random()
        cumulative = 0.0
        for basis, amp in self.amplitudes.items():
            cumulative += abs(amp) ** 2
            if r <= cumulative:
                return basis
        return list(self.amplitudes.keys())[-1]

    def entangle_with(self, other: "QuantumState"):
        for b in self.amplitudes:
            if b in other.amplitudes:
                self.amplitudes[b] *= 0.8
                other.amplitudes[b] *= 0.8

    def to_dict(self) -> dict:
        probs = {b: round(abs(a)**2, 4) for b, a in self.amplitudes.items()}
        return {"probabilities": probs, "collapsed_to": self.measure()}


class QuantumSuperpositionEngine:
    def __init__(self, seed=42):
        self.seed = seed
        self.states: dict[str, QuantumState] = {}
        self.measurements: list[dict] = []
        self.basis = ["active", "dormant", "evolving", "stable", "unstable"]

    def add_module(self, name: str):
        self.states[name] = QuantumState(self.basis, seed=hash(name) % 10000)

    def measure_all(self) -> list[dict]:
        self.measurements = []
        for name, state in self.states.items():
            result = state.measure()
            self.measurements.append({"module": name, "collapsed_to": result, "probabilities": {b: round(state.probability(b), 4) for b in self.basis}})
        return self.measurements

    def find_coherent_pairs(self, threshold: float = 0.5) -> list[dict]:
        pairs = []
        names = list(self.states.keys())
        for i, a in enumerate(names):
            for b in names[i+1:]:
                coherence = sum(
                    self.states[a].probability(basis) * self.states[b].probability(basis)
                    for basis in self.basis
                )
                if coherence > threshold:
                    pairs.append({"a": a, "b": b, "coherence": round(coherence, 4)})
        pairs.sort(key=lambda x: x["coherence"], reverse=True)
        return pairs[:10]

    def report(self) -> dict:
        self.measure_all()
        state_counts = {}
        for m in self.measurements:
            state_counts[m["collapsed_to"]] = state_counts.get(m["collapsed_to"], 0) + 1
        return {
            "engine": "quantum_superposition_engine",
            "modules": len(self.states),
            "state_distribution": state_counts,
            "coherent_pairs": self.find_coherent_pairs(),
        }


def demo():
    engine = QuantumSuperpositionEngine(seed=42)
    for py in list((ROOT / "lab").glob("*.py"))[:8]:
        if not py.name.startswith("_"):
            engine.add_module(py.stem)
    for py in list((ROOT / "api").glob("*.py"))[:5]:
        if not py.name.startswith("_"):
            engine.add_module(py.stem)
    return engine.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
