"""Economy domain — resource exchange between agents."""
from __future__ import annotations

from collections import defaultdict
from typing import Any


class EconomyDomain:
    def __init__(self) -> None:
        self._balances: dict[str, float] = defaultdict(float)
        self._prices: dict[str, float] = defaultdict(lambda: 1.0)

    def credit(self, agent_id: str, amount: float) -> None:
        self._balances[agent_id] += amount

    def debit(self, agent_id: str, amount: float) -> bool:
        if self._balances[agent_id] < amount:
            return False
        self._balances[agent_id] -= amount
        return True

    def transfer(self, from_id: str, to_id: str, amount: float) -> bool:
        if self.debit(from_id, amount):
            self.credit(to_id, amount)
            return True
        return False

    @property
    def ledger(self) -> dict[str, float]:
        return {k: round(v, 4) for k, v in sorted(self._balances.items(), key=lambda x: -x[1])}

    @property
    def gini(self) -> float:
        vals = sorted(self._balances.values())
        n = len(vals)
        if n == 0 or sum(vals) == 0:
            return 0.0
        cumsum = sum((i + 1) * v for i, v in enumerate(vals))
        return round((2 * cumsum) / (n * sum(vals)) - (n + 1) / n, 4)
