"""Dream Catcher — Captures and analyzes the system's "dreams" (random explorations).

Runs random experiments in parallel, captures unexpected outputs, and
builds a dream journal that the system can learn from.
"""
from __future__ import annotations
import hashlib
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Dream:
    def __init__(self, seed: int):
        self.seed = seed
        self.rng = random.Random(seed)
        self.content = self._generate()
        self.lucidity = self.rng.random()
        self.timestamp = time.time()

    def _generate(self) -> dict:
        themes = ["fractal_growth", "quantum_entanglement", "entropy_reversal",
                   "agent_communion", "realm_fusion", "signal_propagation"]
        theme = self.rng.choice(themes)
        intensity = self.rng.random()
        imagery = []
        for _ in range(self.rng.randint(2, 5)):
            imagery.append({
                "element": self.rng.choice(["spiral", "wave", "node", "edge", "field", "pulse"]),
                "color": self.rng.choice(["violet", "cyan", "emerald", "gold", "crimson"]),
                "intensity": round(self.rng.random(), 3),
            })
        return {"theme": theme, "intensity": round(intensity, 3), "imagery": imagery}

    def to_dict(self) -> dict:
        return {
            "seed": self.seed,
            "content": self.content,
            "lucidity": round(self.lucidity, 3),
            "timestamp": self.timestamp,
        }


class DreamCatcher:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.dreams: list[Dream] = []
        self.journal: list[dict] = []

    def catch_dream(self) -> Dream:
        dream = Dream(self.seed + len(self.dreams))
        self.dreams.append(dream)
        return dream

    def analyze(self) -> dict:
        if not self.dreams:
            return {"message": "no dreams captured"}
        themes = {}
        for d in self.dreams:
            t = d.content["theme"]
            themes[t] = themes.get(t, 0) + 1
        avg_lucidity = sum(d.lucidity for d in self.dreams) / len(self.dreams)
        return {
            "dream_count": len(self.dreams),
            "themes": themes,
            "avg_lucidity": round(avg_lucidity, 3),
            "most_common_theme": max(themes, key=themes.get) if themes else None,
        }

    def report(self) -> dict:
        analysis = self.analyze()
        return {
            "dream_catcher": "dream_catcher",
            "analysis": analysis,
            "dreams": [d.to_dict() for d in self.dreams[:5]],
        }


def demo():
    catcher = DreamCatcher(seed=42)
    for _ in range(15):
        catcher.catch_dream()
    return catcher.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
