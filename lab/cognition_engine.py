"""Cognition Engine — Integrates dream_cycle, morphic_field, and memetic_engine.

Provides a unified cognitive processing pipeline for agents.
"""
from __future__ import annotations
import hashlib
import random
import time
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class DreamFragment:
    def __init__(self, symbol: str, frequency: int, confidence: float):
        self.symbol = symbol
        self.frequency = frequency
        self.confidence = confidence


class DreamCycle:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.fragments: list[DreamFragment] = []
        self.dreams: list[dict] = []

    def enter_dream(self, memories: list[dict]) -> dict:
        symbols = []
        for mem in memories:
            for key in mem:
                symbols.append(key)
        counts = Counter(symbols)
        fragments = []
        for sym, freq in counts.most_common(10):
            conf = min(1.0, freq / max(1, len(memories)) * self.rng.uniform(0.8, 1.2))
            fragments.append(DreamFragment(sym, freq, round(conf, 4)))
        self.fragments = fragments
        insight = {
            "fragment_count": len(fragments),
            "top_symbol": fragments[0].symbol if fragments else None,
            "consolidation": round(sum(f.confidence for f in fragments) / max(1, len(fragments)), 4),
            "timestamp": time.time(),
        }
        self.dreams.append(insight)
        return insight


class MorphicField:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.field_strength: dict[str, float] = {}
        self.connections: list[tuple[str, str]] = []

    def register_pattern(self, name: str, strength: float = 0.5):
        self.field_strength[name] = strength

    def resonate(self, pattern_a: str, pattern_b: str) -> float:
        if pattern_a in self.field_strength and pattern_b in self.field_strength:
            resonance = (self.field_strength[pattern_a] + self.field_strength[pattern_b]) / 2
            self.connections.append((pattern_a, pattern_b))
            return resonance
        return 0.0

    def evolve(self):
        for name in self.field_strength:
            drift = random.Random(hash(name + str(time.time()))).uniform(-0.05, 0.05)
            self.field_strength[name] = max(0, min(1, self.field_strength[name] + drift))


class MemeticEngine:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.mememes: dict[str, dict] = {}
        self.generation = 0

    def inject_meme(self, name: str, fitness: float, tags: list[str]):
        self.mememes[name] = {"fitness": fitness, "tags": tags, "offspring": 0}

    def evolve(self, generations: int = 5):
        for g in range(generations):
            self.generation += 1
            for name, meme in self.mememes.items():
                mutation = random.Random(hash(name + str(self.generation))).uniform(-0.1, 0.1)
                meme["fitness"] = max(0, min(1, meme["fitness"] + mutation))
                if meme["fitness"] > 0.7:
                    meme["offspring"] += 1


class CognitionEngine:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.dream_cycle = DreamCycle(seed)
        self.morphic_field = MorphicField(seed)
        self.memetic_engine = MemeticEngine(seed)
        self.processing_log: list[dict] = []

    def process(self, memories: list[dict], patterns: list[str]) -> dict:
        dream = self.dream_cycle.enter_dream(memories)
        for p in patterns:
            self.morphic_field.register_pattern(p, random.Random(hash(p)).uniform(0.3, 0.9))
        for i in range(len(patterns) - 1):
            self.morphic_field.resonate(patterns[i], patterns[i + 1])
        self.morphic_field.evolve()
        for p in patterns:
            self.memetic_engine.inject_meme(p, random.Random(hash(p)).uniform(0.4, 0.8), ["cognition"])
        self.memetic_engine.evolve(generations=3)
        result = {
            "dream": dream,
            "morphic_connections": len(self.morphic_field.connections),
            "meme_count": len(self.memetic_engine.mememes),
            "avg_fitness": round(
                sum(m["fitness"] for m in self.memetic_engine.mememes.values()) /
                max(1, len(self.memetic_engine.mememes)), 4
            ),
        }
        self.processing_log.append(result)
        return result

    def report(self) -> dict:
        return {
            "engine": "cognition_engine",
            "dreams_had": len(self.dream_cycle.dreams),
            "morphic_patterns": len(self.morphic_field.field_strength),
            "morphic_connections": len(self.morphic_field.connections),
            "meme_generation": self.memetic_engine.generation,
            "active_memes": len(self.memetic_engine.mememes),
        }


def demo():
    engine = CognitionEngine(seed=42)
    memories = [
        {"action": "move", "result": "success", "energy": 0.9},
        {"action": "scan", "result": "anomaly", "threat": 7},
        {"action": "build", "result": "success", "structure": "bridge"},
        {"action": "move", "result": "blocked", "energy": 0.7},
        {"action": "scan", "result": "clear", "energy": 0.8},
    ]
    patterns = ["alpha_pattern", "beta_pattern", "gamma_pattern", "delta_pattern"]
    result = engine.process(memories, patterns)
    return {"cognition": engine.report(), "last_process": result}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
