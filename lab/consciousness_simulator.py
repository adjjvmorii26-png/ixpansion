"""Consciousness Simulator — Emergent awareness from simple rules.

Models consciousness as an emergent property of interconnected simple
agents following basic rules. No single agent is "aware" — but the
system as a whole develops self-referential behavior.
"""
from __future__ import annotations
import hashlib
import random
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class Neuron:
    """A single neuron in the consciousness substrate."""

    def __init__(self, neuron_id: int, seed: int = 42):
        self.id = neuron_id
        self.activation = 0.0
        self.threshold = 0.5
        self.connections: list[int] = []
        self.weight: float = random.Random(seed + neuron_id).uniform(0.1, 1.0)
        self.fired_count = 0
        self.membrane_potential = 0.0

    def connect(self, target_id: int, weight: float = 0.5):
        self.connections.append(target_id)

    def receive(self, signal: float):
        self.membrane_potential += signal * self.weight

    def fire(self) -> float:
        if self.membrane_potential >= self.threshold:
            self.activation = min(1.0, self.membrane_potential)
            self.fired_count += 1
            self.membrane_potential = 0.0
            return self.activation
        self.activation *= 0.9  # Decay
        self.membrane_potential *= 0.8
        return 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id, "activation": round(self.activation, 4),
            "fired": self.fired_count, "connections": len(self.connections),
        }


class ConsciousnessSubstrate:
    """The neural substrate from which consciousness emerges."""

    def __init__(self, size: int = 50, seed: int = 42):
        self.neurons: dict[int, Neuron] = {}
        self.tick_count = 0
        self.awareness_level = 0.0
        self.self_reference_count = 0
        self.global_workspace: list[dict] = []
        self.rng = random.Random(seed)

        # Create neurons
        for i in range(size):
            self.neurons[i] = Neuron(i, seed)

        # Create connections (small-world network)
        for i in range(size):
            n_connections = self.rng.randint(2, 5)
            targets = self.rng.sample(range(size), min(n_connections, size - 1))
            for t in targets:
                if t != i:
                    self.neurons[i].connect(t, self.rng.uniform(0.2, 0.8))

    def stimulate(self, neuron_id: int, intensity: float = 1.0):
        if neuron_id in self.neurons:
            self.neurons[neuron_id].receive(intensity)

    def global_broadcast(self, signal: float):
        """Broadcast to all neurons — the global workspace."""
        for neuron in self.neurons.values():
            neuron.receive(signal * 0.1)

    def tick(self) -> dict:
        self.tick_count += 1
        fired = 0
        total_activation = 0.0

        # Phase 1: All neurons fire simultaneously
        fire_outputs = {}
        for nid, neuron in self.neurons.items():
            output = neuron.fire()
            if output > 0:
                fired += 1
                fire_outputs[nid] = output
                total_activation += output

        # Phase 2: Propagate
        for nid, output in fire_outputs.items():
            for target_id in self.neurons[nid].connections:
                if target_id in self.neurons:
                    self.neurons[target_id].receive(output * 0.3)

        # Phase 3: Global workspace — if enough neurons fire, broadcast
        if fired > len(self.neurons) * 0.3:
            self.global_broadcast(0.5)
            self.global_workspace.append({
                "tick": self.tick_count, "fired": fired,
                "level": "conscious" if fired > len(self.neurons) * 0.5 else "pre-conscious",
            })

        # Phase 4: Self-reference detection
        high_activation = sum(1 for n in self.neurons.values() if n.activation > 0.7)
        if high_activation > len(self.neurons) * 0.2:
            self.self_reference_count += 1

        # Phase 5: Update awareness
        self.awareness_level = min(1.0, (self.self_reference_count / max(1, self.tick_count)) * 10)

        return {
            "tick": self.tick_count,
            "fired": fired,
            "total_neurons": len(self.neurons),
            "avg_activation": round(total_activation / max(1, len(self.neurons)), 4),
            "high_activation": high_activation,
            "awareness": round(self.awareness_level, 4),
            "workspace_events": len(self.global_workspace),
        }

    def simulate(self, ticks: int = 50) -> dict:
        results = []
        # Initial stimulation
        for i in range(min(10, len(self.neurons))):
            self.stimulate(i, self.rng.uniform(0.5, 1.0))

        for _ in range(ticks):
            # Random external stimuli
            if self.tick_count % 5 == 0:
                target = self.rng.randint(0, len(self.neurons) - 1)
                self.stimulate(target, self.rng.uniform(0.3, 0.8))
            results.append(self.tick())

        return {
            "ticks": ticks,
            "final_awareness": round(self.awareness_level, 4),
            "total_fired": sum(r["fired"] for r in results),
            "workspace_events": len(self.global_workspace),
            "self_references": self.self_reference_count,
            "consciousness_levels": [r["level"] for r in self.global_workspace[-5:]],
        }

    def report(self) -> dict:
        return {
            "substrate": "consciousness_substrate",
            "neurons": len(self.neurons),
            "tick": self.tick_count,
            "awareness": round(self.awareness_level, 4),
            "self_references": self.self_reference_count,
            "workspace_events": len(self.global_workspace),
        }


def demo():
    substrate = ConsciousnessSubstrate(size=40, seed=42)
    sim = substrate.simulate(ticks=50)
    return {"simulation": sim, "report": substrate.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
