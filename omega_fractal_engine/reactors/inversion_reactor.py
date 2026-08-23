"""Reverses logic flows — flips boolean states and inverts numeric relationships."""
from __future__ import annotations

from typing import Any


class InversionReactor:
    def __init__(self) -> None:
        self._inversions = 0

    def invert(self, state: dict[str, Any]) -> dict[str, Any]:
        """Flip booleans, negate numerics, reverse strings."""
        result = {}
        for key, val in state.items():
            if isinstance(val, bool):
                result[key] = not val
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                result[key] = -val
            elif isinstance(val, str):
                result[key] = val[::-1]
            elif isinstance(val, list):
                result[key] = val[::-1]
            else:
                result[key] = val
            self._inversions += 1
        return result

    def invert_rules(self, rules: list[tuple[callable, str]]) -> list[tuple[callable, str]]:
        """Negate rule predicates and flip conclusions."""
        inverted = []
        for pred, conclusion in rules:
            inverted.append((lambda ctx, p=pred: not p(ctx), f"NOT({conclusion})"))
            self._inversions += 1
        return inverted

    @property
    def total_inversions(self) -> int:
        return self._inversions
