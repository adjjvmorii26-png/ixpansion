"""Merges behaviors — combines two behavioral profiles into one."""
from __future__ import annotations

import random
from typing import Any


class FusionReactor:
    def __init__(self) -> None:
        self._fusions = 0

    def fuse(self, behavior_a: dict[str, float],
             behavior_b: dict[str, float],
             bias: float = 0.5) -> dict[str, float]:
        """Blend two behaviors with a bias weight (0=all A, 1=all B)."""
        fused: dict[str, float] = {}
        all_keys = set(behavior_a) | set(behavior_b)
        for key in sorted(all_keys):
            va = behavior_a.get(key, 0.5)
            vb = behavior_b.get(key, 0.5)
            blended = va * (1 - bias) + vb * bias
            fused[key] = round(max(0.0, min(1.0, blended)), 6)
        self._fusions += 1
        return fused

    @property
    def total_fusions(self) -> int:
        return self._fusions
