"""Culture domain — shared norms, traditions, collective memory."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


class CultureDomain:
    def __init__(self) -> None:
        self._norms: dict[str, float] = {}  # norm_name -> strength
        self._traditions: dict[str, list[str]] = defaultdict(list)
        self._collective_memory: list[dict[str, Any]] = []

    def establish_norm(self, name: str, initial_strength: float = 0.3) -> None:
        self._norms[name] = max(0.0, min(1.0, initial_strength))

    def reinforce_norm(self, name: str, agent_id: str, amount: float = 0.05) -> bool:
        if name not in self._norms:
            return False
        self._norms[name] = min(1.0, self._norms[name] + amount)
        return True

    def violate_norm(self, name: str, agent_id: str) -> float:
        """Returns social penalty incurred."""
        if name not in self._norms:
            return 0.0
        penalty = self._norms[name] * 0.2
        self._norms[name] = max(0.0, self._norms[name] - 0.01)
        return penalty

    def record_tradition(self, tradition: str, participant: str) -> None:
        self._traditions[tradition].append(participant)

    @property
    def strong_norms(self) -> list[str]:
        return [n for n, s in self._norms.items() if s >= 0.7]

    @property
    def summary(self) -> dict[str, Any]:
        return {
            "norms": {k: round(v, 3) for k, v in sorted(self._norms.items(), key=lambda x: -x[1])},
            "traditions": {t: len(members) for t, members in self._traditions.items()},
            "memories": len(self._collective_memory),
        }
