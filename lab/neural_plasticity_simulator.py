"""Neural Plasticity Simulator — Adapts connections based on usage patterns.

Models how the codebase's neural pathways strengthen or weaken based on
how often they're traversed, creating a self-organizing network that
optimizes itself over time.
"""
from __future__ import annotations
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Synapse:
    def __init__(self, source: str, target: str, weight: float = 0.5):
        self.source = source
        self.target = target
        self.weight = weight
        self.activations = 0
        self.last_used = 0

    def activate(self, tick: int):
        self.weight = min(1.0, self.weight + 0.05)
        self.activations += 1
        self.last_used = tick

    def decay(self):
        self.weight = max(0.01, self.weight * 0.995)

    def to_dict(self) -> dict:
        return {
            "source": self.source, "target": self.target,
            "weight": round(self.weight, 4),
            "activations": self.activations,
        }


class NeuralPlasticitySimulator:
    def __init__(self, seed=42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.synapses: dict[tuple[str, str], Synapse] = {}
        self.regions: dict[str, dict] = {}
        self.tick_count = 0

    def add_region(self, name: str, neurons: int = 5):
        self.regions[name] = {"neurons": neurons, "activity": 0.0}

    def connect_regions(self, a: str, b: str, weight: float = 0.3):
        key = (a, b)
        if key not in self.synapses:
            self.synapses[key] = Synapse(a, b, weight)

    def auto_connect(self):
        names = list(self.regions.keys())
        for i, a in enumerate(names):
            for b in names[i+1:]:
                if self.rng.random() < 0.4:
                    self.connect_regions(a, b, self.rng.uniform(0.2, 0.8))

    def tick(self):
        self.tick_count += 1
        # Random activation pattern
        active_regions = self.rng.sample(
            list(self.regions.keys()),
            min(3, len(self.regions))
        )
        for region in active_regions:
            self.regions[region]["activity"] = min(1.0, self.regions[region]["activity"] + 0.2)

        # Propagate through synapses
        for key, synapse in self.synapses.items():
            if synapse.source in active_regions:
                synapse.activate(self.tick_count)
            synapse.decay()

        # Decay region activity
        for region in self.regions:
            self.regions[region]["activity"] *= 0.9

    def simulate(self, ticks=30):
        for _ in range(ticks):
            self.tick()
        strong = [s for s in self.synapses.values() if s.weight > 0.7]
        weak = [s for s in self.synapses.values() if s.weight < 0.1]
        return {
            "ticks": ticks,
            "total_synapses": len(self.synapses),
            "strong_connections": len(strong),
            "weak_connections": len(weak),
            "avg_weight": round(
                sum(s.weight for s in self.synapses.values()) / max(1, len(self.synapses)), 4
            ),
        }

    def report(self) -> dict:
        return {
            "simulator": "neural_plasticity_simulator",
            "regions": len(self.regions),
            "synapses": len(self.synapses),
            "tick": self.tick_count,
            "top_synapses": [s.to_dict() for s in sorted(
                self.synapses.values(), key=lambda s: s.weight, reverse=True
            )[:5]],
        }


def demo():
    sim = NeuralPlasticitySimulator(seed=42)
    for name in ["api", "lab", "bridges", "constellation", "mycelium", "sandbox"]:
        sim.add_region(name, neurons=5)
    sim.auto_connect()
    result = sim.simulate(ticks=30)
    return {"simulation": result, "report": sim.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
