"""Randomness + chaos injection — controlled entropy source."""
from __future__ import annotations

import random
import hashlib
from typing import Any


class EntropySource:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._seed = seed

    @property
    def seed(self) -> int | None:
        return self._seed

    def float(self, lo: float = 0.0, hi: float = 1.0) -> float:
        return self._rng.uniform(lo, hi)

    def int(self, lo: int, hi: int) -> int:
        return self._rng.randint(lo, hi)

    def choice(self, seq: list[Any]) -> Any:
        return self._rng.choice(seq)

    def shuffle(self, seq: list[Any]) -> list[Any]:
        result = list(seq)
        self._rng.shuffle(result)
        return result

    def gauss(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        return self._rng.gauss(mu, sigma)

    def chaos_inject(self, target: dict[str, Any], magnitude: float = 0.1) -> dict[str, Any]:
        """Perturb all numeric values in a state dict."""
        for key, val in target.items():
            if isinstance(val, (int, float)) and not key.startswith("_"):
                noise = self._rng.gauss(0, magnitude * max(abs(val), 1))
                target[key] = val + noise
        return target

    def deterministic_hash(self, data: str) -> str:
        return hashlib.sha256(f"{self._seed}:{data}".encode()).hexdigest()[:16]
