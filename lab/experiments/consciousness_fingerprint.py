#!/usr/bin/env python3
"""Consciousness Fingerprint — unique run signatures from all subsystems.

Produces a holistic "fingerprint" of a system run by sampling from:
- Mycelium hyphae states
- Omega kernel pulse values
- Constellation braid configurations
- Ixpansion agent dispatch counts
- Bridge event log hashes

The fingerprint is a multi-dimensional vector that uniquely identifies
this exact configuration. No two runs produce the same fingerprint
(unless the seed is identical).

Use cases:
- Detect when a system has drifted from a known-good state
- Compare two runs to see if they converged
- Create "birth certificates" for new agents
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SubsystemSample:
    """A sample from one subsystem."""
    source: str
    metrics: dict[str, float]
    event_count: int = 0
    last_event_hash: str = ""

    @property
    def sample_hash(self) -> str:
        raw = json.dumps(self.metrics, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()[:12]


@dataclass
class Fingerprint:
    """A holistic system fingerprint."""
    run_id: str
    vector: dict[str, float]
    magnitude: float
    subsystem_hashes: dict[str, str]
    composite_hash: str
    birth_certificate: str

    def payload(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "vector": {k: round(v, 6) for k, v in self.vector.items()},
            "magnitude": round(self.magnitude, 6),
            "subsystem_hashes": self.subsystem_hashes,
            "composite_hash": self.composite_hash,
            "birth_certificate": self.birth_certificate,
        }

    def distance(self, other: "Fingerprint") -> float:
        """Hamming distance between composite hashes."""
        return sum(a != b for a, b in zip(self.composite_hash, other.composite_hash))

    def cosine_similarity(self, other: "Fingerprint") -> float:
        keys = sorted(set(self.vector) | set(other.vector))
        dot = sum(self.vector.get(k, 0) * other.vector.get(k, 0) for k in keys)
        mag_a = math.sqrt(sum(v * v for v in self.vector.values()))
        mag_b = math.sqrt(sum(v * v for v in other.vector.values()))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)


@dataclass
class FingerprintEngine:
    """Collects subsystem samples and produces fingerprints."""
    seed: int | None = None
    components: list[str] = field(default_factory=lambda: [
        "mycelium", "omega", "constellation", "ixpansion", "bridges",
    ])

    def __post_init__(self) -> None:
        import random
        self._rng = random.Random(self.seed)
        self._run_counter = 0

    def sample_subsystem(self, name: str, metrics: dict[str, float],
                         event_count: int = 0, last_event_hash: str = "") -> SubsystemSample:
        return SubsystemSample(
            source=name,
            metrics=metrics,
            event_count=event_count,
            last_event_hash=last_event_hash,
        )

    def fingerprint(self, samples: list[SubsystemSample], run_id: str | None = None) -> Fingerprint:
        """Produce a fingerprint from a set of subsystem samples."""
        self._run_counter += 1
        run_id = run_id or f"run-{self._run_counter:04d}"

        # Build unified vector from all samples
        vector: dict[str, float] = {}
        subsystem_hashes: dict[str, str] = {}

        for sample in samples:
            prefix = sample.source
            for key, value in sample.metrics.items():
                vector[f"{prefix}.{key}"] = value
            if sample.event_count:
                vector[f"{prefix}.event_density"] = float(sample.event_count)
            subsystem_hashes[prefix] = sample.sample_hash

        # Add cross-subsystem relations
        sources = [s.source for s in samples]
        for i, s_a in enumerate(samples):
            for s_b in samples[i + 1:]:
                # Correlation between subsystems
                shared_keys = set(s_a.metrics) & set(s_b.metrics)
                if shared_keys:
                    avg_corr = sum(
                        1.0 - abs(s_a.metrics[k] - s_b.metrics[k])
                        for k in shared_keys
                    ) / len(shared_keys)
                    vector[f"rel.{s_a.source}.{s_b.source}"] = round(avg_corr, 6)

        # Composite hash
        composite_raw = json.dumps(
            {"run_id": run_id, **{k: round(v, 4) for k, v in sorted(vector.items())}},
            separators=(",", ":"),
        )
        composite_hash = hashlib.sha256(composite_raw.encode()).hexdigest()

        magnitude = math.sqrt(sum(v * v for v in vector.values()))

        # Birth certificate: a human-readable summary
        dominant = max(vector, key=lambda k: abs(vector[k])) if vector else "none"
        birth_certificate = (
            f"Run {run_id} | {len(samples)} subsystems | "
            f"dominant={dominant}({vector.get(dominant, 0):.3f}) | "
            f"magnitude={magnitude:.3f} | "
            f"composite={composite_hash[:16]}"
        )

        return Fingerprint(
            run_id=run_id,
            vector=vector,
            magnitude=magnitude,
            subsystem_hashes=subsystem_hashes,
            composite_hash=composite_hash,
            birth_certificate=birth_certificate,
        )

    def drift_analysis(self, sequence: list[Fingerprint]) -> dict[str, Any]:
        """Analyze how fingerprints drift over a sequence of runs."""
        if len(sequence) < 2:
            return {"status": "insufficient_data"}

        distances = []
        similarities = []
        for i in range(len(sequence) - 1):
            d = sequence[i].distance(sequence[i + 1])
            s = sequence[i].cosine_similarity(sequence[i + 1])
            distances.append(d)
            similarities.append(s)

        return {
            "sequence_length": len(sequence),
            "mean_distance": round(sum(distances) / len(distances), 4),
            "max_distance": max(distances),
            "mean_similarity": round(sum(similarities) / len(similarities), 4),
            "min_similarity": round(min(similarities), 4),
            "trend": "diverging" if distances[-1] > distances[0] else "converging",
            "stable": max(distances) - min(distances) < 10,
        }


def demo() -> dict[str, Any]:
    engine = FingerprintEngine(seed=42)

    # Simulate 5 runs with slight metric variations
    sequence: list[Fingerprint] = []
    for i in range(5):
        samples = [
            engine.sample_subsystem("mycelium", {
                "hyphae_count": 10 + i * 0.5,
                "signal_strength": 0.7 - i * 0.02,
                "consent_rate": 0.85 + i * 0.01,
            }, event_count=20 + i),
            engine.sample_subsystem("omega", {
                "pulse_frequency": 1.0,
                "entropy_level": 0.3 + i * 0.05,
                "superposition_depth": 3 - i * 0.2,
            }),
            engine.sample_subsystem("constellation", {
                "braid_count": 5 + i,
                "treaty_coverage": 0.9,
                "atlas_size": 100 + i * 10,
            }),
            engine.sample_subsystem("ixpansion", {
                "active_agents": 3 + i,
                "hex_operations": 50 - i * 3,
                "mutation_rate": 0.1 + i * 0.02,
            }),
            engine.sample_subsystem("bridges", {
                "bridge_count": 14,
                "kintsugi_repairs": 2 + i,
                "resonance_score": 0.6 + i * 0.03,
            }),
        ]
        fp = engine.fingerprint(samples, run_id=f"run-{i:04d}")
        sequence.append(fp)

    drift = engine.drift_analysis(sequence)

    return {
        "fingerprints": [fp.payload() for fp in sequence],
        "drift_analysis": drift,
    }


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
