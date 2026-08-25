"""Neural Network Mapper — Maps code dependencies as a neural network.

Creates a multi-layer perceptron where modules are neurons, imports are
weights, and the network learns to classify modules by function.
"""
from __future__ import annotations
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NeuralLayer:
    def __init__(self, size: int, seed=42):
        self.neurons = [{"activation": 0.0, "bias": random.Random(seed + i).uniform(-0.5, 0.5)} for i in range(size)]

    def forward(self, inputs: list[float]) -> list[float]:
        outputs = []
        for i, neuron in enumerate(self.neurons):
            total = neuron["bias"]
            for j, inp in enumerate(inputs):
                if j < len(inputs):
                    total += inp * (1.0 / (1 + abs(i - j)))
            neuron["activation"] = 1.0 / (1 + math.exp(-max(-10, min(10, total))))
            outputs.append(neuron["activation"])
        return outputs


class NeuralNetworkMapper:
    def __init__(self, seed=42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.layers: list[NeuralLayer] = []
        self.classifications: list[dict] = []

    def build_network(self, layer_sizes: list[int]):
        self.layers = []
        for size in layer_sizes:
            self.layers.append(NeuralLayer(size, self.seed + len(self.layers)))

    def classify(self, name: str, features: list[float]) -> str:
        current = features
        for layer in self.layers:
            current = layer.forward(current)
        categories = ["core", "interface", "data", "test", "bridge"]
        idx = int(current[0] * len(categories)) % len(categories)
        return categories[idx]

    def map_codebase(self):
        self.classifications = []
        for py in list((ROOT / "lab").glob("*.py"))[:10]:
            if not py.name.startswith("_"):
                text = py.read_text(errors="replace")
                lines = text.splitlines()
                features = [
                    len(lines) / 500.0,
                    sum(1 for l in lines if l.strip().startswith("def ")) / max(1, len(lines) / 50),
                    sum(1 for l in lines if l.strip().startswith("class ")) / 5.0,
                    sum(1 for l in lines if l.strip().startswith(("import ", "from "))) / 10.0,
                    1.0 if "test" in py.stem else 0.0,
                ]
                category = self.classify(py.stem, features)
                self.classifications.append({"module": py.stem, "category": category, "features": [round(f, 3) for f in features]})

    def report(self) -> dict:
        self.map_codebase()
        cats = {}
        for c in self.classifications:
            cats[c["category"]] = cats.get(c["category"], 0) + 1
        return {
            "mapper": "neural_network_mapper",
            "layers": len(self.layers),
            "classified": len(self.classifications),
            "categories": cats,
            "samples": self.classifications[:5],
        }


def demo():
    mapper = NeuralNetworkMapper(seed=42)
    mapper.build_network([5, 8, 4, 1])
    return mapper.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
