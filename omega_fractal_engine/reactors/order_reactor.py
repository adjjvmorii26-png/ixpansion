"""Injects structure into the system."""
from __future__ import annotations

import math
from typing import Any


class OrderReactor:
    def __init__(self) -> None:
        self._normalizations = 0

    def normalize(self, target_state: dict[str, Any]) -> dict[str, Any]:
        """Snap values toward nearest 'clean' values (integers or round fractions)."""
        for key, value in list(target_state.items()):
            if isinstance(value, float):
                # Snap to nearest 0.25 increment if close enough
                snapped = round(value * 4) / 4
                if abs(value - snapped) < 0.05:
                    target_state[key] = snapped
                    self._normalizations += 1
        return target_state

    def enforce_symmetry(self, positions: list[tuple[float, ...]]) -> list[tuple[float, ...]]:
        """Mirror all positions around the origin to enforce geometric symmetry."""
        mirrored = []
        for pos in positions:
            neg = tuple(-x for x in pos)
            if neg not in positions:
                mirrored.append(neg)
                self._normalizations += 1
        return positions + mirrored

    @property
    def total_normalizations(self) -> int:
        return self._normalizations
