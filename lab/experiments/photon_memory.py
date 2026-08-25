from __future__ import annotations
"""Photon Memory — interference-pattern based information storage.

Memories are stored as simulated photon interference patterns (complex
amplitude arrays). Writing a memory produces a wave pattern; reading
requires superposing a reference wave to reconstruct the original signal.
Lossless if the reference matches; degrades gracefully with noise.
"""
import math
import cmath
import hashlib
import json
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class PhotonWave:
    wavelength: float
    amplitude: float
    phase: float
    samples: int = 256

    def evaluate(self) -> List[complex]:
        result = []
        for i in range(self.samples):
            t = i / self.samples
            angle = 2 * math.pi * t * (1 / self.wavelength) + self.phase
            result.append(complex(
                self.amplitude * math.cos(angle),
                self.amplitude * math.sin(angle)
            ))
        return result

@dataclass
class InterferenceMemory:
    label: str
    pattern: List[complex]
    wavelength: float
    phase: float
    checksum: str = ""

    def __post_init__(self):
        if not self.checksum:
            raw = "".join(f"{p.real:.6f}{p.imag:.6f}" for p in self.pattern)
            self.checksum = hashlib.sha256(raw.encode()).hexdigest()[:16]


class PhotonMemoryEngine:
    def __init__(self, base_wavelength: float = 1.0, noise_level: float = 0.0):
        self.base_wavelength = base_wavelength
        self.noise_level = noise_level
        self.memories: dict[str, InterferenceMemory] = {}
        self.wave_pool: List[PhotonWave] = []

    def _text_to_wave_params(self, text: str) -> Tuple[float, float]:
        digest = hashlib.sha256(text.encode()).hexdigest()
        wavelength = (int(digest[:8], 16) % 1000 + 100) / 1000.0
        phase = (int(digest[8:16], 16) % 10000) / 10000.0 * 2 * math.pi
        return wavelength, phase

    def _encode_signal(self, text: str) -> List[complex]:
        bits = "".join(format(b, "08b") for b in text.encode("utf-8"))
        wave_params = self._text_to_wave_params(text)
        wave = PhotonWave(
            wavelength=wave_params[0],
            amplitude=1.0,
            phase=wave_params[1],
            samples=max(256, len(bits) * 4)
        )
        carrier = wave.evaluate()
        result = []
        for i, bit in enumerate(bits):
            idx = i % len(carrier)
            signal = carrier[idx] * (1.0 if bit == "1" else -1.0)
            result.append(signal)
        self.wave_pool.append(wave)
        return result

    def store(self, label: str, text: str) -> InterferenceMemory:
        pattern = self._encode_signal(text)
        wavelength, phase = self._text_to_wave_params(text)
        mem = InterferenceMemory(
            label=label, pattern=pattern,
            wavelength=wavelength, phase=phase
        )
        self.memories[label] = mem
        return mem

    def read(self, label: str, reference_wavelength: float | None = None) -> float:
        if label not in self.memories:
            return 0.0
        mem = self.memories[label]
        wl = reference_wavelength or mem.wavelength
        ref_wave = PhotonWave(
            wavelength=wl, amplitude=1.0,
            phase=mem.phase, samples=len(mem.pattern)
        )
        reference = ref_wave.evaluate()
        correlation = 0.0
        for i in range(min(len(mem.pattern), len(reference))):
            val = mem.pattern[i] * reference[i].conjugate()
            correlation += val.real
        norm = max(abs(correlation) / len(mem.pattern), 1e-10)
        if self.noise_level > 0:
            import random
            noise = random.gauss(0, self.noise_level)
            norm = max(0, norm + noise)
        return norm

    def fidelity(self, label: str) -> float:
        return self.read(label)

    def interference_map(self, labels: List[str]) -> List[Tuple[str, str, float]]:
        results = []
        for i, a in enumerate(labels):
            for b in labels[i + 1:]:
                if a in self.memories and b in self.memories:
                    pa = self.memories[a].pattern
                    pb = self.memories[b].pattern
                    cross = sum(
                        (pa[j] * pb[j].conjugate()).real
                        for j in range(min(len(pa), len(pb)))
                    )
                    results.append((a, b, cross / max(len(pa), 1)))
        return results

    def export_state(self) -> dict:
        return {
            "memory_count": len(self.memories),
            "wavelengths": {
                k: v.wavelength for k, v in self.memories.items()
            },
            "wave_pool_size": len(self.wave_pool),
        }


def demo():
    engine = PhotonMemoryEngine(base_wavelength=1.0)
    test_messages = [
        ("consciousness", "The engine dreams in interference patterns"),
        ("identity", "Each run generates a unique photon signature"),
        ("evolution", "Memories evolve through wave interaction"),
        ("void", "In the absence of signal, noise becomes meaning"),
    ]
    print("=== Photon Memory Engine ===")
    for label, msg in test_messages:
        mem = engine.store(label, msg)
        fidelity = engine.fidelity(label)
        print(f"  Stored '{label}': {len(mem.pattern)} samples, "
              f"fidelity={fidelity:.4f}, checksum={mem.checksum}")

    print("\nInterference map:")
    for a, b, cross in engine.interference_map(list(engine.memories.keys())):
        print(f"  {a} <-> {b}: cross-correlation={cross:.4f}")

    print("\nWrong-reference read test:")
    wrong = engine.read("consciousness", reference_wavelength=9.9)
    correct = engine.read("consciousness")
    print(f"  Correct ref: {correct:.4f}, Wrong ref: {wrong:.4f}")

    state = engine.export_state()
    print(f"\nState: {json.dumps(state, indent=2)}")
    return state


if __name__ == "__main__":
    demo()
