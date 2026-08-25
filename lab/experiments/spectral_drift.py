#!/usr/bin/env python3
"""Spectral Drift Engine — consciousness state drift using superposition + mycelium substrate.

Agents enter superposition with multiple possible temperaments. Over ticks,
the drift engine simulates how their "spectral fingerprint" evolves as
amplitudes interfere. The result is a drift trajectory — a sequence of
state snapshots that reveal whether an agent trends toward order, chaos,
or a strange attractor between them.

This bridges omega_prime superposition with mycelium substrate gradients
to create emergent personality evolution.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SpectralState:
    """A single snapshot of an agent's consciousness spectrum."""
    tick: int
    agent_id: str
    amplitudes: dict[str, float]
    drift_magnitude: float
    entropy: float
    dominant_trait: str
    fingerprint: str

    def payload(self) -> dict[str, Any]:
        return {
            "tick": self.tick,
            "agent_id": self.agent_id,
            "amplitudes": self.amplitudes,
            "drift_magnitude": round(self.drift_magnitude, 6),
            "entropy": round(self.entropy, 6),
            "dominant_trait": self.dominant_trait,
            "fingerprint": self.fingerprint,
        }


def _fingerprint(amplitudes: dict[str, float], tick: int) -> str:
    raw = json.dumps({"a": amplitudes, "t": tick}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _entropy(amplitudes: dict[str, float]) -> float:
    """Shannon entropy of the amplitude distribution."""
    total = sum(abs(v) for v in amplitudes.values())
    if total == 0:
        return 0.0
    probs = [abs(v) / total for v in amplitudes.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)


def _dominant(amplitudes: dict[str, float]) -> str:
    if not amplitudes:
        return "void"
    return max(amplitudes, key=lambda k: abs(amplitudes[k]))


@dataclass
class DriftEngine:
    """Simulates spectral drift across ticks.

    Each tick, amplitudes are perturbed by:
    1. Interference (crosstalk between traits)
    2. Damping (extreme values decay toward median)
    3. Noise injection (random walk component)
    """
    traits: list[str] = field(default_factory=lambda: [
        "order", "chaos", "empathy", "calculation", "memory", "vision",
    ])
    interference_strength: float = 0.05
    damping_factor: float = 0.02
    noise_scale: float = 0.03
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def initialize(self, agent_id: str, amplitudes: dict[str, float] | None = None) -> list[SpectralState]:
        """Create initial state and drift trajectory."""
        if amplitudes is None:
            amplitudes = {t: 1.0 / len(self.traits) for t in self.traits}
        trajectory = [self._snapshot(0, agent_id, amplitudes)]
        return trajectory

    def drift(self, agent_id: str, states: list[SpectralState], ticks: int = 5) -> list[SpectralState]:
        """Extend trajectory by N drift ticks."""
        if not states:
            return self.initialize(agent_id)
        current = dict(states[-1].amplitudes)
        trajectory = list(states)

        for i in range(ticks):
            tick = trajectory[-1].tick + 1
            current = self._perturb(current)
            trajectory.append(self._snapshot(tick, agent_id, current))

        return trajectory

    def _perturb(self, amplitudes: dict[str, float]) -> dict[str, float]:
        traits = list(amplitudes.keys())
        result = dict(amplitudes)

        # Interference: each trait pulls slightly toward every other trait's amplitude
        for i, t1 in enumerate(traits):
            for t2 in traits[i + 1:]:
                coupling = self._rng.uniform(-self.interference_strength, self.interference_strength)
                diff = amplitudes[t2] - amplitudes[t1]
                result[t1] += coupling * diff
                result[t2] -= coupling * diff

        # Damping: pull toward mean
        mean_amp = sum(result.values()) / len(result) if result else 0
        for t in traits:
            result[t] = result[t] - self.damping_factor * (result[t] - mean_amp)

        # Noise
        for t in traits:
            result[t] += self._rng.gauss(0, self.noise_scale)

        # Normalize to [0, 1]
        for t in traits:
            result[t] = max(0.0, min(1.0, result[t]))

        return result

    def _snapshot(self, tick: int, agent_id: str, amplitudes: dict[str, float]) -> SpectralState:
        prev_amp = {t: 1.0 / len(self.traits) for t in self.traits} if tick == 0 else None
        drift_mag = 0.0
        if prev_amp is not None:
            drift_mag = sum(abs(amplitudes.get(t, 0) - prev_amp.get(t, 0)) for t in self.traits)

        return SpectralState(
            tick=tick,
            agent_id=agent_id,
            amplitudes={t: round(amplitudes[t], 6) for t in sorted(amplitudes)},
            drift_magnitude=drift_mag,
            entropy=_entropy(amplitudes),
            dominant_trait=_dominant(amplitudes),
            fingerprint=_fingerprint(amplitudes, tick),
        )

    def analyze_trajectory(self, trajectory: list[SpectralState]) -> dict[str, Any]:
        """Summarize a drift trajectory."""
        if not trajectory:
            return {"status": "empty"}

        entropies = [s.entropy for s in trajectory]
        drift_mags = [s.drift_magnitude for s in trajectory]
        traits_seen = [s.dominant_trait for s in trajectory]

        return {
            "agent_id": trajectory[0].agent_id,
            "ticks": len(trajectory),
            "entropy_range": [round(min(entropies), 4), round(max(entropies), 4)],
            "mean_drift": round(sum(drift_mags) / len(drift_mags), 6) if drift_mags else 0,
            "dominant_history": traits_seen,
            "converged": max(entropies) - min(entropies) < 0.1,
            "signature": _fingerprint(trajectory[-1].amplitudes, trajectory[-1].tick),
        }


def demo() -> dict[str, Any]:
    engine = DriftEngine(seed=42)
    states = engine.initialize("agent-0", {"order": 0.8, "chaos": 0.2, "empathy": 0.5})
    states = engine.drift("agent-0", states, ticks=20)
    analysis = engine.analyze_trajectory(states)
    return {
        "trajectory_length": len(states),
        "analysis": analysis,
        "final_state": states[-1].payload(),
    }


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
