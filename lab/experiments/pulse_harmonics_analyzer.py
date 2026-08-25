#!/usr/bin/env python3
"""Pulse Harmonics Analyzer — detect rhythmic patterns in system oscillations.

Bridges pulse_harmonics + time_crystal + entropy to analyze the
rhythmic heartbeat of the system. Detects:
- Fundamental frequency (the primary pulse rate)
- Harmonics (multiples of the fundamental)
- Phase relationships between subsystems
- Entropy modulation patterns (does chaos follow a rhythm?)

This is the system's stethoscope — it listens to its own heartbeat
and reports what it hears.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PulseSample:
    tick: int
    source: str
    value: float
    phase: float = 0.0


@dataclass
class Harmonic:
    frequency: float
    amplitude: float
    phase: float
    source: str
    overtone_number: int

    def payload(self) -> dict[str, Any]:
        return {
            "frequency": round(self.frequency, 4),
            "amplitude": round(self.amplitude, 4),
            "phase": round(self.phase, 4),
            "source": self.source,
            "overtone": self.overtone_number,
        }


@dataclass
class PulseHarmonicsAnalyzer:
    """Analyze rhythmic patterns across system oscillations."""
    sample_rate: int = 1  # samples per tick
    min_peak_distance: int = 2
    amplitude_threshold: float = 0.01

    def __post_init__(self) -> None:
        self._samples: dict[str, list[PulseSample]] = defaultdict(list)
        self._tick = 0

    def record(self, source: str, value: float) -> None:
        self._tick += 1
        self._samples[source].append(PulseSample(
            tick=self._tick, source=source, value=value,
            phase=(self._tick * 2 * math.pi / max(1, self._find_period(source))) % (2 * math.pi)
        ))

    def _find_period(self, source: str) -> int:
        """Simple autocorrelation to find dominant period."""
        values = [s.value for s in self._samples.get(source, [])]
        if len(values) < 4:
            return 4
        mean = sum(values) / len(values)
        centered = [v - mean for v in values]
        best_period = 4
        best_corr = -1.0
        for period in range(2, min(len(centered) // 2, 30)):
            corr = 0.0
            count = 0
            for i in range(len(centered) - period):
                corr += centered[i] * centered[i + period]
                count += 1
            if count > 0:
                corr /= count
                if corr > best_corr:
                    best_corr = corr
                    best_period = period
        return best_period

    def analyze(self, source: str) -> dict[str, Any]:
        samples = self._samples.get(source, [])
        if len(samples) < 4:
            return {"source": source, "status": "insufficient_data", "samples": len(samples)}

        values = [s.value for s in samples]
        period = self._find_period(source)
        mean_val = sum(values) / len(values)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        amplitude = math.sqrt(variance) * 2

        # Find peaks
        peaks: list[int] = []
        for i in range(1, len(values) - 1):
            if values[i] > values[i - 1] and values[i] > values[i + 1]:
                if values[i] > mean_val + self.amplitude_threshold:
                    peaks.append(i)

        # Harmonic analysis via simple DFT
        harmonics: list[Harmonic] = []
        n = len(values)
        if n > 0:
            for k in range(1, min(n // 2, 30)):
                real = sum(values[i] * math.cos(2 * math.pi * k * i / n) for i in range(n))
                imag = sum(values[i] * math.sin(2 * math.pi * k * i / n) for i in range(n))
                amp = math.sqrt(real ** 2 + imag ** 2) / n
                phase = math.atan2(imag, real)
                if amp > self.amplitude_threshold * 0.1:
                    harmonics.append(Harmonic(
                        frequency=k / max(1, period),
                        amplitude=amp,
                        phase=phase,
                        source=source,
                        overtone_number=k,
                    ))

        # Phase coherence
        if len(samples) > period:
            cycle_phases = [s.phase for s in samples[-period:]]
            phase_variance = sum((p - sum(cycle_phases) / len(cycle_phases)) ** 2
                                 for p in cycle_phases) / len(cycle_phases)
            coherence = max(0.0, 1.0 - phase_variance)
        else:
            coherence = 0.5

        return {
            "source": source,
            "samples": len(samples),
            "period": period,
            "frequency": round(1.0 / max(1, period), 4),
            "mean_value": round(mean_val, 4),
            "amplitude": round(amplitude, 4),
            "peak_count": len(peaks),
            "coherence": round(coherence, 4),
            "harmonics": [h.payload() for h in harmonics[:5]],
            "entropy_modulation": round(
                max(0.0, min(1.0, amplitude * coherence)), 4
            ),
            "analysis_signature": hashlib.sha256(
                json.dumps({"source": source, "period": period, "peaks": len(peaks)}).encode()
            ).hexdigest()[:12],
        }

    def cross_source_phase(self) -> dict[str, Any]:
        """Analyze phase relationships between different sources."""
        sources = list(self._samples.keys())
        if len(sources) < 2:
            return {"status": "need_multiple_sources"}

        correlations: dict[str, float] = {}
        for i, s_a in enumerate(sources):
            for s_b in sources[i + 1:]:
                a_vals = [s.value for s in self._samples[s_a]]
                b_vals = [s.value for s in self._samples[s_b]]
                min_len = min(len(a_vals), len(b_vals))
                if min_len < 2:
                    continue
                a_centered = [v - sum(a_vals[:min_len]) / min_len for v in a_vals[:min_len]]
                b_centered = [v - sum(b_vals[:min_len]) / min_len for v in b_vals[:min_len]]
                dot = sum(a * b for a, b in zip(a_centered, b_centered))
                mag_a = math.sqrt(sum(a ** 2 for a in a_centered))
                mag_b = math.sqrt(sum(b ** 2 for b in b_centered))
                corr = dot / (mag_a * mag_b) if mag_a > 0 and mag_b > 0 else 0
                pair = f"{s_a}<->{s_b}"
                correlations[pair] = round(corr, 4)

        return correlations


def demo() -> dict[str, Any]:
    analyzer = PulseHarmonicsAnalyzer()

    import random
    rng = random.Random(42)

    # Simulate 3 subsystems with different rhythms
    for tick in range(60):
        # Heartbeat at period 4
        analyzer.record("heartbeat", 0.5 + 0.4 * math.sin(2 * math.pi * tick / 4) + rng.gauss(0, 0.05))
        # Mycelium at period 7
        analyzer.record("mycelium", 0.3 + 0.5 * math.sin(2 * math.pi * tick / 7) + rng.gauss(0, 0.08))
        # Entropy at period 12
        analyzer.record("entropy", 0.4 + 0.3 * math.sin(2 * math.pi * tick / 12) + rng.gauss(0, 0.03))

    analyses = {source: analyzer.analyze(source) for source in ["heartbeat", "mycelium", "entropy"]}
    phase_relations = analyzer.cross_source_phase()

    return {
        "analyses": analyses,
        "cross_source_phase": phase_relations,
    }


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
