"""Injects randomness into the system."""
from __future__ import annotations

import random
from typing import Any


class ChaosReactor:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._injections = 0

    def inject(self, target_state: dict[str, Any], magnitude: float = 0.1) -> dict[str, Any]:
        """Randomly perturb numeric values in the state."""
        for key, value in list(target_state.items()):
            if isinstance(value, (int, float)) and not key.startswith("_"):
                noise = self._rng.gauss(0, magnitude * abs(value) if value else magnitude)
                target_state[key] = value + noise
                self._injections += 1
            elif isinstance(value, str) and self._rng.random() < magnitude:
                pos = self._rng.randint(0, max(len(value) - 1, 0))
                chars = "abcdefghijklmnopqrstuvwxyz✦◆◇"
                target_state[key] = value[:pos] + self._rng.choice(chars) + value[pos+1:]
                self._injections += 1
        return target_state

    @property
    def total_injections(self) -> int:
        return self._injections
