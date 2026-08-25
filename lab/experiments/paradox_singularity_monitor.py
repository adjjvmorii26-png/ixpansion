#!/usr/bin/env python3
"""Paradox Singularity Monitor — detect when paradoxes collapse into catastrophe.

When multiple paradox signatures from different modules begin converging
on the same trait space, they risk forming a "singularity" — a
self-reinforcing loop that amplifies contradictions exponentially.

The monitor tracks:
- Paradox density in trait space
- Convergence rate between paradoxes
- Singularity risk score
- Recommended intervention (diversify, isolate, or amplify)

This is the system's immune response to its own self-referential loops.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParadoxSignature:
    sig_id: str
    source_module: str
    traits: dict[str, float]
    severity: float
    birth_tick: int
    age_ticks: int = 0

    @property
    def magnitude(self) -> float:
        return math.sqrt(sum(v * v for v in self.traits.values()))

    def distance_to(self, other: "ParadoxSignature") -> float:
        all_keys = set(self.traits) | set(other.traits)
        return math.sqrt(
            sum((self.traits.get(k, 0) - other.traits.get(k, 0)) ** 2 for k in all_keys)
        )

    def payload(self) -> dict[str, Any]:
        return {
            "sig_id": self.sig_id,
            "source": self.source_module,
            "traits": {k: round(v, 3) for k, v in self.traits.items()},
            "severity": round(self.severity, 3),
            "magnitude": round(self.magnitude, 3),
            "age": self.age_ticks,
        }


@dataclass
class SingularityEvent:
    event_id: str
    involved_paradoxes: list[str]
    center_of_mass: dict[str, float]
    risk_score: float
    recommendation: str
    tick: int

    def payload(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "paradoxes": self.involved_paradoxes,
            "center": {k: round(v, 3) for k, v in self.center_of_mass.items()},
            "risk": round(self.risk_score, 3),
            "recommendation": self.recommendation,
            "tick": self.tick,
        }


@dataclass
class ParadoxSingularityMonitor:
    """Detect paradox convergence into singularities."""
    convergence_threshold: float = 0.3
    singularity_threshold: float = 0.7
    min_paradoxes_for_singularity: int = 3
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = __import__("random").Random(self.seed)
        self._paradoxes: dict[str, ParadoxSignature] = {}
        self._singularities: list[SingularityEvent] = []
        self._tick = 0
        self._density_history: list[dict[str, Any]] = []

    def register_paradox(self, sig_id: str, source: str,
                         traits: dict[str, float], severity: float = 0.5) -> ParadoxSignature:
        sig = ParadoxSignature(
            sig_id=sig_id, source_module=source,
            traits=traits, severity=severity, birth_tick=self._tick,
        )
        self._paradoxes[sig_id] = sig
        return sig

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        new_singularities: list[dict[str, Any]] = []

        # Age all paradoxes
        for sig in self._paradoxes.values():
            sig.age_ticks += 1

        # Compute pairwise distances
        sigs = list(self._paradoxes.values())
        if len(sigs) >= self.min_paradoxes_for_singularity:
            # Find clusters of close paradoxes
            clusters = self._find_clusters(sigs)

            for cluster in clusters:
                if len(cluster) >= self.min_paradoxes_for_singularity:
                    # Compute center of mass
                    all_traits = set()
                    for sig in cluster:
                        all_traits.update(sig.traits.keys())

                    center = {}
                    for trait in all_traits:
                        center[trait] = sum(sig.traits.get(trait, 0) for sig in cluster) / len(cluster)

                    # Compute risk score
                    avg_distance = sum(
                        sig.distance_to(cluster[0]) for sig in cluster[1:]
                    ) / max(1, len(cluster) - 1)
                    avg_severity = sum(sig.severity for sig in cluster) / len(cluster)
                    density = len(cluster) / max(1, len(sigs))

                    risk = (
                        max(0.0, 1.0 - avg_distance) * 0.4 +
                        avg_severity * 0.3 +
                        density * 0.3
                    )

                    if risk >= self.singularity_threshold:
                        recommendation = self._recommend(risk, cluster)
                        event = SingularityEvent(
                            event_id=hashlib.sha256(
                                f"singularity:{self._tick}:{len(self._singularities)}".encode()
                            ).hexdigest()[:12],
                            involved_paradoxes=[s.sig_id for s in cluster],
                            center_of_mass=center,
                            risk_score=risk,
                            recommendation=recommendation,
                            tick=self._tick,
                        )
                        self._singularities.append(event)
                        new_singularities.append(event.payload())

        # Record density
        self._density_history.append({
            "tick": self._tick,
            "paradox_count": len(sigs),
            "mean_severity": round(
                sum(s.severity for s in sigs) / max(1, len(sigs)), 3
            ),
            "singularities": len(self._singularities),
        })

        return {"tick": self._tick, "new_singularities": len(new_singularities)}

    def _find_clusters(self, sigs: list[ParadoxSignature]) -> list[list[ParadoxSignature]]:
        """Simple distance-based clustering."""
        used: set[str] = set()
        clusters: list[list[ParadoxSignature]] = []

        for i, sig_a in enumerate(sigs):
            if sig_a.sig_id in used:
                continue
            cluster = [sig_a]
            used.add(sig_a.sig_id)
            for sig_b in sigs[i + 1:]:
                if sig_b.sig_id in used:
                    continue
                if sig_a.distance_to(sig_b) < self.convergence_threshold:
                    cluster.append(sig_b)
                    used.add(sig_b.sig_id)
            if len(cluster) >= 2:
                clusters.append(cluster)

        return clusters

    def _recommend(self, risk: float, cluster: list[ParadoxSignature]) -> str:
        if risk >= 0.9:
            return "isolate_and_neutralize"
        elif risk >= 0.8:
            return "diversify_trait_space"
        elif risk >= 0.7:
            return "amplify_differences"
        return "monitor_closely"

    def monitor_report(self) -> dict[str, Any]:
        sigs = list(self._paradoxes.values())
        return {
            "tick": self._tick,
            "total_paradoxes": len(sigs),
            "total_singularities": len(self._singularities),
            "mean_severity": round(
                sum(s.severity for s in sigs) / max(1, len(sigs)), 3
            ),
            "mean_magnitude": round(
                sum(s.magnitude for s in sigs) / max(1, len(sigs)), 3
            ),
            "density_history": self._density_history[-5:],
            "recent_singularities": [s.payload() for s in self._singularities[-3:]],
        }


def demo() -> dict[str, Any]:
    monitor = ParadoxSingularityMonitor(seed=42)

    # Create paradoxes with some convergence
    trait_sets = [
        {"self_reference": 0.8, "negation": 0.6, "temporal": 0.3},
        {"self_reference": 0.75, "negation": 0.55, "temporal": 0.35},
        {"self_reference": 0.7, "negation": 0.65, "temporal": 0.25},
        {"self_reference": 0.2, "negation": 0.1, "temporal": 0.9},
        {"self_reference": 0.15, "negation": 0.15, "temporal": 0.85},
    ]

    sources = ["module_a", "module_b", "module_c", "module_d", "module_e"]
    for i, (traits, source) in enumerate(zip(trait_sets, sources)):
        monitor.register_paradox(f"p{i}", source, traits, severity=0.5 + i * 0.05)

    for _ in range(10):
        monitor.tick()

    return monitor.monitor_report()


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
