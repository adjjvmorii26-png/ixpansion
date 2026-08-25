#!/usr/bin/env python3
"""Cross-Pollinator — a unifying bridge protocol across all subsystems.

Ingests signals from multiple sources (mycelium hyphae, omega pulses,
constellation braids, ixpansion agents) and discovers cross-domain
correlations that no single subsystem could see.

The pollinator maintains a "pollen map" — a latent space where each
signal is projected based on its features. When two signals from
different sources land near each other, the pollinator emits a
"cross-pollination event" — a new synthetic signal that combines
elements of both.

This creates emergent connections between otherwise isolated subsystems.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Signal:
    """A signal from any subsystem."""
    source: str
    label: str
    features: dict[str, float]
    tick: int
    origin_id: str = ""

    @property
    def signal_id(self) -> str:
        raw = f"{self.source}:{self.label}:{self.tick}:{self.origin_id}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]


@dataclass(frozen=True)
class PollenPoint:
    """A signal projected into the latent pollen space."""
    signal: Signal
    coordinates: tuple[float, ...]
    cluster_id: int = -1


@dataclass(frozen=True)
class CrossPollination:
    """A synthetic signal born from two parent signals."""
    child_id: str
    parent_a_id: str
    parent_b_id: str
    parent_a_source: str
    parent_b_source: str
    child_label: str
    child_features: dict[str, float]
    novelty: float
    tick: int

    def payload(self) -> dict[str, Any]:
        return {
            "child_id": self.child_id,
            "parents": [self.parent_a_id, self.parent_b_id],
            "sources": [self.parent_a_source, self.parent_b_source],
            "label": self.child_label,
            "features": self.child_features,
            "novelty": round(self.novelty, 4),
            "tick": self.tick,
        }


def _feature_vector(features: dict[str, float], all_keys: list[str]) -> tuple[float, ...]:
    return tuple(features.get(k, 0.0) for k in all_keys)


def _euclidean(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _cosine(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


@dataclass
class CrossPollinator:
    """Discovers cross-domain correlations between subsystem signals."""
    proximity_threshold: float = 1.5
    max_pollinations_per_tick: int = 5
    novelty_threshold: float = 0.05
    seed: int | None = None

    def __post_init__(self) -> None:
        import random
        self._rng = random.Random(self.seed)
        self._all_keys: list[str] = []
        self._points: list[PollenPoint] = []
        self._pollinations: list[CrossPollination] = []
        self._tick = 0

    def ingest(self, signals: list[Signal]) -> list[CrossPollination]:
        """Ingest signals and discover cross-pollinations."""
        # Update feature keys
        for sig in signals:
            for k in sig.features:
                if k not in self._all_keys:
                    self._all_keys.append(k)
        self._all_keys.sort()

        # Project signals into pollen space
        new_points = []
        for sig in signals:
            coords = _feature_vector(sig.features, self._all_keys)
            new_points.append(PollenPoint(signal=sig, coordinates=coords))
        self._points.extend(new_points)

        # Discover cross-pollinations between different sources
        new_pollinations: list[CrossPollination] = []
        seen_pairs: set[tuple[str, str]] = set()

        for i, p_a in enumerate(new_points):
            for j, p_b in enumerate(self._points):
                if p_a.signal.source == p_b.signal.source:
                    continue
                if p_a.signal.signal_id == p_b.signal.signal_id:
                    continue
                pair_key = tuple(sorted([p_a.signal.signal_id, p_b.signal.signal_id]))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                dist = _euclidean(p_a.coordinates, p_b.coordinates)
                if dist > self.proximity_threshold:
                    continue

                # Check cross-source diversity
                if len(new_pollinations) >= self.max_pollinations_per_tick:
                    break

                child = self._cross_pollinate(p_a.signal, p_b.signal)
                if child.novelty >= self.novelty_threshold:
                    new_pollinations.append(child)
                    self._pollinations.append(child)

        self._tick += 1
        return new_pollinations

    def _cross_pollinate(self, a: Signal, b: Signal) -> CrossPollination:
        """Create a child signal from two parent signals."""
        all_keys = sorted(set(a.features) | set(b.features))
        child_features: dict[str, float] = {}

        for k in all_keys:
            a_val = a.features.get(k, 0.0)
            b_val = b.features.get(k, 0.0)
            # Dominant gene + recessive blend
            if self._rng.random() > 0.5:
                child_features[k] = max(a_val, b_val)
            else:
                alpha = self._rng.uniform(0.3, 0.7)
                child_features[k] = alpha * a_val + (1 - alpha) * b_val

        # Novelty: how different is child from both parents?
        child_vec = _feature_vector(child_features, self._all_keys) if self._all_keys else ()
        a_vec = _feature_vector(a.features, self._all_keys) if self._all_keys else ()
        b_vec = _feature_vector(b.features, self._all_keys) if self._all_keys else ()

        # Use normalized Euclidean distance as novelty metric
        # This captures feature-level differences better than cosine
        max_possible = math.sqrt(len(self._all_keys)) if self._all_keys else 1.0
        dist_a = _euclidean(child_vec, a_vec) / max_possible if child_vec and a_vec else 0
        dist_b = _euclidean(child_vec, b_vec) / max_possible if child_vec and b_vec else 0
        novelty = (dist_a + dist_b) / 2

        child_label = f"{a.label}×{b.label}"
        child_id = hashlib.sha256(
            f"{a.signal_id}:{b.signal_id}:{child_label}".encode()
        ).hexdigest()[:12]

        return CrossPollination(
            child_id=child_id,
            parent_a_id=a.signal_id,
            parent_b_id=b.signal_id,
            parent_a_source=a.source,
            parent_b_source=b.source,
            child_label=child_label,
            child_features={k: round(v, 4) for k, v in child_features.items()},
            novelty=round(novelty, 4),
            tick=self._tick,
        )

    def summary(self) -> dict[str, Any]:
        source_pairs = set()
        for p in self._pollinations:
            pair = tuple(sorted([p.parent_a_source, p.parent_b_source]))
            source_pairs.add(pair)

        return {
            "total_signals": len(self._points),
            "total_pollinations": len(self._pollinations),
            "cross_source_connections": len(source_pairs),
            "source_pairs": [list(pair) for pair in sorted(source_pairs)],
            "mean_novelty": (
                round(sum(p.novelty for p in self._pollinations) / len(self._pollinations), 4)
                if self._pollinations else 0
            ),
        }


def demo() -> dict[str, Any]:
    pollinator = CrossPollinator(seed=42)

    batch_1 = [
        Signal(source="mycelium", label="nutrient_pulse", features={"energy": 0.8, "reach": 0.3, "decay": 0.1}, tick=0, origin_id="hypha-1"),
        Signal(source="mycelium", label="spore_release", features={"energy": 0.4, "reach": 0.9, "decay": 0.3}, tick=0, origin_id="hypha-2"),
        Signal(source="omega", label="pulse_tick", features={"energy": 0.7, "amplitude": 0.5, "frequency": 0.6}, tick=0, origin_id="kernel-0"),
        Signal(source="constellation", label="braid_signal", features={"energy": 0.6, "constellation": 0.8, "formation": 0.2}, tick=0, origin_id="constellation-a"),
        Signal(source="ixpansion", label="hex_dispatch", features={"energy": 0.5, "opcode": 0.7, "reach": 0.4}, tick=0, origin_id="hex-vm-1"),
    ]

    batch_2 = [
        Signal(source="omega", label="superposition_collapse", features={"energy": 0.9, "amplitude": 0.2, "frequency": 0.8}, tick=1, origin_id="kernel-1"),
        Signal(source="mycelium", label="consent_exchange", features={"energy": 0.6, "reach": 0.5, "trust": 0.8}, tick=1, origin_id="hypha-3"),
        Signal(source="ixpansion", label="mutation_event", features={"energy": 0.3, "opcode": 0.5, "entropy": 0.9}, tick=1, origin_id="hex-vm-2"),
    ]

    pollinations_batch1 = pollinator.ingest(batch_1)
    pollinations_batch2 = pollinator.ingest(batch_2)

    return {
        "batch_1_pollinations": len(pollinations_batch1),
        "batch_2_pollinations": len(pollinations_batch2),
        "summary": pollinator.summary(),
        "sample_children": [p.payload() for p in (pollinations_batch1 + pollinations_batch2)[:3]],
    }


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
