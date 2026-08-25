from __future__ import annotations
"""Dream Weaver — generates synthetic dreams from system state patterns.

Transforms raw system telemetry into narrative dream sequences. Each dream
is a symbolic interpretation of module interactions, entropy states, and
anomaly patterns. Dreams can be compared, archived, and used to predict
future system behavior through pattern recognition.
"""
import math
import random
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

SYMBOLS = {
    "high_entropy": ["storm", "chaos", "tornado", "wildfire", "flood"],
    "low_entropy": ["calm", "crystal", "ice", "stone", "silence"],
    "connection": ["bridge", "thread", "root", "river", "signal"],
    "isolation": ["island", "void", "desert", "fog", "shadow"],
    "growth": ["bloom", "tree", "wave", "flame", "cloud"],
    "decay": ["rust", "dust", "ash", "fossil", "echo"],
    "tension": ["spring", "bow", "thread", "wire", "storm"],
    "harmony": ["chord", "dance", "orbit", "spiral", "weave"],
}

@dataclass
class DreamSymbol:
    symbol: str
    category: str
    intensity: float
    position: int

@dataclass
class DreamSequence:
    seed: str
    symbols: List[DreamSymbol]
    narrative: str
    emotional_tone: str
    entropy_signature: float
    timestamp: float
    clarity: float = 0.0

    def __post_init__(self):
        if not self.narrative:
            words = [s.symbol for s in self.symbols]
            self.narrative = " ".join(words)

class DreamWeaver:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.dream_archive: List[DreamSequence] = []
        self.dream_count = 0

    def _system_to_entropy(self, state: Dict) -> float:
        values = []
        for v in state.values():
            if isinstance(v, (int, float)):
                values.append(abs(v))
            elif isinstance(v, dict):
                values.extend(abs(vv) for vv in v.values() if isinstance(vv, (int, float)))
        if not values:
            return 0.5
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return min(1.0, math.sqrt(variance) / max(mean, 0.001))

    def _classify_state(self, entropy: float, state: Dict) -> Dict[str, float]:
        classifications = {}
        if entropy > 0.7:
            classifications["high_entropy"] = entropy
            classifications["tension"] = entropy * 0.8
        elif entropy < 0.3:
            classifications["low_entropy"] = 1.0 - entropy
            classifications["harmony"] = 1.0 - entropy
        else:
            classifications["connection"] = 0.5
            classifications["growth"] = 0.5

        if state.get("failures", 0) > 0:
            classifications["decay"] = min(1.0, state["failures"] / 10.0)
        if state.get("connections", 0) > 5:
            classifications["connection"] = min(1.0, state["connections"] / 20.0)
        if state.get("temperature", 20) > 50:
            classifications["tension"] = min(1.0, state["temperature"] / 100.0)
        return classifications

    def weave(self, state: Dict, dream_id: str = None) -> DreamSequence:
        self.dream_count += 1
        if dream_id is None:
            dream_id = f"dream_{self.dream_count:04d}"

        entropy = self._system_to_entropy(state)
        classifications = self._classify_state(entropy, state)

        symbols = []
        position = 0
        for category, intensity in sorted(classifications.items(),
                                           key=lambda x: x[1], reverse=True):
            pool = SYMBOLS.get(category, SYMBOLS["connection"])
            chosen = self.rng.choice(pool)
            symbols.append(DreamSymbol(
                symbol=chosen, category=category,
                intensity=intensity, position=position
            ))
            position += 1

        tones = ["lucid", "fragmented", "coherent", "nightmarish",
                 "ethereal", "prophetic", "nostalgic", "alien"]
        tone = self.rng.choice(tones)

        clarity = 1.0 - entropy * 0.5 + self.rng.uniform(-0.1, 0.1)
        clarity = max(0.0, min(1.0, clarity))

        narrative_parts = []
        for s in symbols:
            intensity_word = "faintly" if s.intensity < 0.3 else (
                "vividly" if s.intensity > 0.7 else "softly"
            )
            narrative_parts.append(f"{intensity_word} {s.symbol}")

        narrative = f"In a {tone} dreamscape, {' then '.join(narrative_parts)}."

        dream = DreamSequence(
            seed=dream_id,
            symbols=symbols,
            narrative=narrative,
            emotional_tone=tone,
            entropy_signature=entropy,
            timestamp=self.dream_count,
            clarity=clarity,
        )
        self.dream_archive.append(dream)
        return dream

    def compare_dreams(self, a: int, b: int) -> Dict:
        if a >= len(self.dream_archive) or b >= len(self.dream_archive):
            return {"error": "index out of range"}
        d1, d2 = self.dream_archive[a], self.dream_archive[b]
        cats1 = {s.category for s in d1.symbols}
        cats2 = {s.category for s in d2.symbols}
        shared = cats1 & cats2
        return {
            "dream_a": d1.seed, "dream_b": d2.seed,
            "shared_symbols": list(shared),
            "entropy_diff": abs(d1.entropy_signature - d2.entropy_signature),
            "clarity_diff": abs(d1.clarity - d2.clarity),
            "same_tone": d1.emotional_tone == d2.emotional_tone,
        }

    def dream_journal(self) -> List[Dict]:
        return [
            {"id": d.seed, "tone": d.emotional_tone,
             "entropy": round(d.entropy_signature, 3),
             "clarity": round(d.clarity, 3),
             "symbols": len(d.symbols),
             "narrative": d.narrative}
            for d in self.dream_archive
        ]


def demo():
    weaver = DreamWeaver(seed=42)
    print("=== Dream Weaver ===")

    states = [
        {"entropy": 0.9, "failures": 8, "connections": 3},
        {"entropy": 0.1, "failures": 0, "connections": 15, "temperature": 22},
        {"entropy": 0.5, "failures": 2, "connections": 7, "temperature": 45},
        {"temperature": 80, "failures": 5, "connections": 1},
        {"entropy": 0.3, "connections": 20, "temperature": 30},
    ]
    for i, state in enumerate(states):
        dream = weaver.weave(state)
        print(f"\n  Dream {i+1} ({dream.seed}):")
        print(f"    Tone: {dream.emotional_tone}, Clarity: {dream.clarity:.3f}")
        print(f"    Entropy: {dream.entropy_signature:.3f}")
        print(f"    Symbols: {[s.symbol for s in dream.symbols]}")
        print(f"    Narrative: {dream.narrative}")

    if len(weaver.dream_archive) >= 2:
        comparison = weaver.compare_dreams(0, 1)
        print(f"\n  Dream 1 vs Dream 2:")
        print(f"    Shared: {comparison['shared_symbols']}")
        print(f"    Entropy diff: {comparison['entropy_diff']:.3f}")

    journal = weaver.dream_journal()
    print(f"\n  Total dreams archived: {len(journal)}")

    return {"dreams": len(journal), "journal": journal}


if __name__ == "__main__":
    demo()
