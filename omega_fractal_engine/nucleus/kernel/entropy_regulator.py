"""Controls chaos levels across the entire engine."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EntropyRegulator:
    """Global chaos thermostat with hysteresis to prevent oscillation."""

    target_entropy: float = 0.5      # Desired chaos level (0=order, 1=chaos)
    current_entropy: float = 0.5
    injection_rate: float = 0.02
    dissipation_rate: float = 0.01
    deadband: float = 0.05           # Hysteresis band
    rng_seed: int | None = None
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.rng_seed)

    def inject_chaos(self) -> None:
        self.current_entropy = min(1.0, self.current_entropy + self._rng.uniform(0, self.injection_rate))

    def dissipate(self) -> None:
        self.current_entropy = max(0.0, self.current_entropy - self._rng.uniform(0, self.dissipation_rate))

    def regulate(self) -> dict[str, Any]:
        """One regulation cycle toward target entropy."""
        delta = self.target_entropy - self.current_entropy
        if abs(delta) > self.deadband:
            if delta > 0:
                self.inject_chaos()
            else:
                self.dissipate()
        return {
            "current": round(self.current_entropy, 6),
            "target": self.target_entropy,
            "pressure": round(abs(delta), 6),
            "regime": self.regime,
        }

    @property
    def regime(self) -> str:
        if self.current_entropy < 0.2:
            return "crystalline"
        elif self.current_entropy < 0.4:
            return "ordered"
        elif self.current_entropy < 0.6:
            return "balanced"
        elif self.current_entropy < 0.8:
            return "turbulent"
        return "inferno"

    @property
    def chaos_budget(self) -> float:
        """How much chaos can still be injected before hitting ceiling."""
        return max(0.0, 1.0 - self.current_entropy)

    def set_target(self, value: float) -> None:
        self.target_entropy = max(0.0, min(1.0, value))
