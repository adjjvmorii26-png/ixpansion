"""Dream-state memory consolidation.

When an agent's action cost is zero (idle), it enters a dream state.
During dreaming, recent episodic memories are pattern-matched and
consolidated into semantic knowledge. The agent may discover
correlations it didn't explicitly observe.
"""
from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DreamFragment:
    """A single insight extracted during a dream cycle."""

    symbol: str
    frequency: int
    confidence: float


class DreamCycle:
    def __init__(self) -> None:
        self._dream_log: list[DreamFragment] = []
        self._is_dreaming: bool = False
        self._dream_depth: int = 0

    @property
    def dreaming(self) -> bool:
        return self._is_dreaming

    def enter_dream(self) -> None:
        self._is_dreaming = True
        self._dream_depth += 1

    def exit_dream(self) -> None:
        self._is_dreaming = False

    def consolidate(self, episodic: dict[str, Any], min_support: int = 2) -> list[DreamFragment]:
        """Extract recurring symbols from episodic memory into fragments."""
        if not self._is_dreaming:
            return []

        values = []
        for v in episodic.values():
            if isinstance(v, str):
                values.append(v)
            elif isinstance(v, (int, float)):
                values.append(f"num:{round(v / 10)}")  # Bucket numbers

        counter = Counter(values)
        new_fragments = []
        for symbol, count in counter.items():
            if count >= min_support:
                confidence = min(1.0, count / max(len(values), 1))
                fragment = DreamFragment(symbol=symbol, frequency=count, confidence=confidence)
                if fragment not in self._dream_log or self._get_freq(symbol) < count:
                    new_fragments.append(fragment)

        for frag in new_fragments:
            existing = next((f for f in self._dream_log if f.symbol == frag.symbol), None)
            if existing:
                existing.frequency = frag.frequency
                existing.confidence = frag.confidence
            else:
                self._dream_log.append(frag)

        return new_fragments

    def _get_freq(self, symbol: str) -> int:
        return next((f.frequency for f in self._dream_log if f.symbol == symbol), 0)

    @property
    def insights(self) -> list[dict[str, Any]]:
        return [
            {"symbol": f.symbol, "freq": f.frequency, "conf": round(f.confidence, 3)}
            for f in sorted(self._dream_log, key=lambda x: -x.confidence)
        ]

    @property
    def depth(self) -> int:
        return self._dream_depth
