from __future__ import annotations
"""Morphic Resonance — detects emergent coordination without communication.

When distant modules begin behaving similarly without explicit communication,
this is "morphic resonance." The system detects convergent patterns across
modules, measures synchronization strength, and identifies resonance nodes.
"""
import math
import random
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
from collections import Counter

@dataclass
class ModuleBehavior:
    name: str
    signals: List[float] = field(default_factory=list)
    frequency: float = 1.0
    phase: float = 0.0
    amplitude: float = 1.0
    resonance_score: float = 0.0

    def waveform(self, length: int = 50) -> List[float]:
        return [
            self.amplitude * math.sin(2 * math.pi * self.frequency * t / length + self.phase)
            for t in range(length)
        ]

@dataclass
class ResonancePair:
    module_a: str
    module_b: str
    correlation: float
    phase_offset: float
    resonance_type: str
    confidence: float

class MorphicResonanceDetector:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.modules: Dict[str, ModuleBehavior] = {}
        self.resonance_pairs: List[ResonancePair] = []
        self.resonance_nodes: Dict[str, float] = {}
        self.tick = 0

    def add_module(self, name: str, frequency: float = 1.0,
                   amplitude: float = 1.0, phase: float = None) -> ModuleBehavior:
        if phase is None:
            phase = self.rng.uniform(0, 2 * math.pi)
        module = ModuleBehavior(name=name, frequency=frequency,
                               phase=phase, amplitude=amplitude)
        module.signals = module.waveform()
        self.modules[name] = module
        return module

    def _correlation(self, a: List[float], b: List[float]) -> float:
        n = min(len(a), len(b))
        if n == 0:
            return 0.0
        mean_a = sum(a[:n]) / n
        mean_b = sum(b[:n]) / n
        num = sum((a[i] - mean_a) * (b[i] - mean_b) for i in range(n))
        den_a = math.sqrt(sum((a[i] - mean_a) ** 2 for i in range(n)))
        den_b = math.sqrt(sum((b[i] - mean_b) ** 2 for i in range(n)))
        if den_a == 0 or den_b == 0:
            return 0.0
        return num / (den_a * den_b)

    def _phase_offset(self, a: ModuleBehavior, b: ModuleBehavior) -> float:
        offset = abs(a.phase - b.phase) % (2 * math.pi)
        return min(offset, 2 * math.pi - offset)

    def detect(self, correlation_threshold: float = 0.7) -> List[ResonancePair]:
        self.resonance_pairs.clear()
        names = list(self.modules.keys())

        for i, na in enumerate(names):
            for nb in names[i + 1:]:
                a, b = self.modules[na], self.modules[nb]
                corr = self._correlation(a.signals, b.signals)
                phase_off = self._phase_offset(a, b)

                if abs(corr) >= correlation_threshold:
                    rtype = "sync" if corr > 0 else "anti_sync"
                    confidence = abs(corr) * (1.0 - phase_off / (2 * math.pi))
                    pair = ResonancePair(
                        module_a=na, module_b=nb,
                        correlation=corr, phase_offset=phase_off,
                        resonance_type=rtype, confidence=confidence,
                    )
                    self.resonance_pairs.append(pair)

                    self.resonance_nodes[na] = self.resonance_nodes.get(na, 0) + abs(corr)
                    self.resonance_nodes[nb] = self.resonance_nodes.get(nb, 0) + abs(corr)

        self.resonance_pairs.sort(key=lambda p: p.confidence, reverse=True)
        return self.resonance_pairs

    def perturb(self, name: str, delta_freq: float = 0.1, delta_phase: float = 0.3):
        if name in self.modules:
            m = self.modules[name]
            m.frequency += delta_freq
            m.phase += delta_phase
            m.signals = m.waveform()

    def step(self):
        self.tick += 1
        for m in self.modules.values():
            m.signals = m.waveform()

    def resonance_report(self) -> Dict:
        return {
            "modules": len(self.modules),
            "resonance_pairs": len(self.resonance_pairs),
            "resonance_nodes": {
                k: round(v, 3) for k, v in sorted(
                    self.resonance_nodes.items(), key=lambda x: x[1], reverse=True
                )
            },
            "top_resonances": [
                {"a": p.module_a, "b": p.module_b,
                 "corr": round(p.correlation, 4), "type": p.resonance_type}
                for p in self.resonance_pairs[:5]
            ],
        }


def demo():
    detector = MorphicResonanceDetector(seed=42)
    print("=== Morphic Resonance Detector ===")

    modules_data = [
        ("alpha", 1.0, 1.0, 0.0),
        ("beta", 1.0, 0.8, 0.1),
        ("gamma", 2.0, 1.0, 0.0),
        ("delta", 0.5, 1.0, math.pi),
        ("epsilon", 1.0, 0.9, 0.05),
        ("zeta", 3.0, 1.0, 0.0),
    ]
    for name, freq, amp, phase in modules_data:
        detector.add_module(name, freq, amp, phase)

    pairs = detector.detect(correlation_threshold=0.5)
    print(f"  Resonance pairs found: {len(pairs)}")
    for p in pairs:
        print(f"    {p.module_a} <-> {p.module_b}: corr={p.correlation:.3f}, "
              f"phase={p.phase_offset:.3f}, type={p.resonance_type}")

    print("\nPerturbing 'beta'...")
    detector.perturb("beta", delta_freq=0.5, delta_phase=1.0)
    new_pairs = detector.detect(correlation_threshold=0.5)
    print(f"  After perturbation: {len(new_pairs)} pairs")

    report = detector.resonance_report()
    print(f"\nResonance nodes: {report['resonance_nodes']}")

    return report


if __name__ == "__main__":
    demo()
