"""Entropy spike — sudden burst of chaos injected into the system."""
from __future__ import annotations

import random
from typing import Any


class EntropySpike:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._spikes_triggered = 0

    def trigger(self, state: dict[str, Any], magnitude: float = 1.0) -> dict[str, Any]:
        """Randomly perturb and scramble the state."""
        for key, val in list(state.items()):
            if isinstance(val, (int, float)) and not key.startswith("_"):
                state[key] = val * self._rng.uniform(1 - magnitude, 1 + magnitude)
            elif isinstance(val, list) and magnitude > 0.5:
                self._rng.shuffle(state[key])
            elif isinstance(val, str) and magnitude > 0.7:
                chars = list(val)
                self._rng.shuffle(chars)
                state[key] = "".join(chars)

        self._spikes_triggered += 1
        return state

    @property
    def count(self) -> int:
        return self._spikes_triggered
