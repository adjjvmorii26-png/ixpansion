"""Wave 127 — Complexity Currency.

A currency whose value is determined by computational complexity —
simple transactions are cheap, complex ones are expensive, and the
currency itself evolves as complexity understanding deepens.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class ComplexityCoin:
    """A unit of complexity currency."""

    def __init__(self, value: float, complexity: float):
        self.value = value
        self.complexity = complexity
        self.created = time.time()
        self.mintage = hashlib.sha256(f"coin:{value}:{self.created}".encode()).hexdigest()[:8]

    @property
    def exchange_rate(self) -> float:
        return self.value * (1 + self.complexity)

    def to_dict(self) -> Dict[str, Any]:
        return {"mintage": self.mintage, "value": round(self.value, 4),
                "complexity": round(self.complexity, 4),
                "exchange_rate": round(self.exchange_rate, 4)}


class ComplexityCurrency:
    """Currency based on computational complexity."""

    def __init__(self):
        self._coins: List[ComplexityCoin] = []
        self._ledger: List[Dict[str, Any]] = []
        self._total_minted = 0.0

    def mint(self, value: float, complexity: float) -> ComplexityCoin:
        coin = ComplexityCoin(value, complexity)
        self._coins.append(coin)
        self._total_minted += value
        return coin

    def transfer(self, from_acct: str, to_acct: str, coin: ComplexityCoin) -> Dict[str, Any]:
        record = {"from": from_acct, "to": to_acct, "coin": coin.mintage,
                  "value": coin.value, "complexity": coin.complexity,
                  "timestamp": time.time()}
        self._ledger.append(record)
        return record

    def total_supply(self) -> float:
        return self._total_minted

    def average_complexity(self) -> float:
        if not self._coins:
            return 0.0
        return sum(c.complexity for c in self._coins) / len(self._coins)

    def status(self) -> Dict[str, Any]:
        return {"total_coins": len(self._coins), "total_minted": round(self._total_minted, 4),
                "average_complexity": round(self.average_complexity(), 4),
                "transactions": len(self._ledger)}
