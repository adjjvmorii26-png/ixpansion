"""Quantum Classifier — Classifies code in superposition states.

Modules exist in multiple classification states simultaneously until
"observed" (analyzed), at which point they collapse into a single class.
This reveals hidden relationships between modules.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import math
import random
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class QuantumState:
    def __init__(self, categories: list[str], seed=42):
        self.rng = random.Random(seed)
        self.amplitudes: dict[str, float] = {}
        total = 0.0
        for cat in categories:
            amp = self.rng.random()
            self.amplitudes[cat] = amp
            total += amp * amp
        for cat in self.amplitudes:
            self.amplitudes[cat] /= math.sqrt(total)

    def probability(self, category: str) -> float:
        return self.amplitudes.get(category, 0) ** 2

    def collapse(self) -> str:
        r = self.rng.random()
        cumulative = 0.0
        for cat, amp in self.amplitudes.items():
            cumulative += amp * amp
            if r <= cumulative:
                return cat
        return list(self.amplitudes.keys())[-1]

    def measure(self) -> dict:
        probs = {cat: round(amp ** 2, 4) for cat, amp in self.amplitudes.items()}
        return {"probabilities": probs, "collapsed_to": self.collapse()}


class QuantumClassifier:
    CATEGORIES = ["data", "logic", "interface", "test", "config", "bridge", "experimental"]

    def __init__(self, seed=42):
        self.seed = seed
        self.states: dict[str, QuantumState] = {}
        self.measurements: list[dict] = []

    def register_module(self, name: str, filepath: Path):
        text = filepath.read_text(errors="replace")
        lines = text.splitlines()
        funcs = sum(1 for l in lines if l.strip().startswith("def "))
        classes = sum(1 for l in lines if l.strip().startswith("class "))
        imports = sum(1 for l in lines if l.strip().startswith(("import ", "from ")))
        has_test = "test" in name.lower() or "assert" in text
        has_api = "handler" in text or "request" in text or "response" in text
        has_bridge = "bridge" in name.lower() or "connect" in text

        weights = {
            "data": 1.0 if imports > 5 else 0.3,
            "logic": 1.0 if funcs > 3 and classes > 0 else 0.3,
            "interface": 1.0 if has_api else 0.2,
            "test": 1.0 if has_test else 0.1,
            "config": 1.0 if filepath.suffix == ".yaml" or filepath.suffix == ".json" else 0.1,
            "bridge": 1.0 if has_bridge else 0.2,
            "experimental": 1.0 if "experiments" in str(filepath) else 0.3,
        }

        self.states[name] = QuantumState(self.CATEGORIES, seed=hash(name) % 10000)
        for cat, w in weights.items():
            if cat in self.states[name].amplitudes:
                self.states[name].amplitudes[cat] *= w

    def measure_all(self) -> list[dict]:
        self.measurements = []
        for name, state in self.states.items():
            result = state.measure()
            self.measurements.append({"module": name, **result})
        return self.measurements

    def find_superposed_pairs(self, threshold: float = 0.3) -> list[dict]:
        pairs = []
        names = list(self.states.keys())
        for i, a in enumerate(names):
            for b in names[i+1:]:
                sa, sb = self.states[a], self.states[b]
                overlap = sum(
                    sa.probability(cat) * sb.probability(cat)
                    for cat in self.CATEGORIES
                )
                if overlap > threshold:
                    pairs.append({"a": a, "b": b, "overlap": round(overlap, 4)})
        pairs.sort(key=lambda x: x["overlap"], reverse=True)
        return pairs[:10]

    def report(self) -> dict:
        self.measure_all()
        pairs = self.find_superposed_pairs()
        category_counts = Counter(m["collapsed_to"] for m in self.measurements)
        return {
            "classifier": "quantum_classifier",
            "module_count": len(self.states),
            "measurements": len(self.measurements),
            "category_distribution": dict(category_counts),
            "superposed_pairs": len(pairs),
            "top_pairs": pairs[:5],
        }


def demo():
    qc = QuantumClassifier(seed=42)
    for base in [ROOT / "api", ROOT / "lab" / "experiments", ROOT / "bridges"]:
        if base.exists():
            for py in base.glob("*.py"):
                if not py.name.startswith("_") and not py.name.startswith("test_"):
                    qc.register_module(py.stem, py)
    return qc.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
