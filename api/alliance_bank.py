"""Wave 138 — Alliance Bank.

A shared financial institution for the federation. Realms deposit
reserves, the bank issues cross-realm credit backed by pooled
reserves, and it maintains a stability ratio to prevent any single
realm from overdrawing the federation.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class AllianceBank:
    """Pooled cross-realm reserves and credit issuance."""

    def __init__(self, reserve_ratio: float = 0.2):
        self.reserve_ratio = max(0.0, min(1.0, reserve_ratio))
        self._reserves: Dict[str, float] = {}
        self._credit_outstanding: Dict[str, float] = {}
        self._defaults = 0

    def deposit(self, realm: str, amount: float) -> float:
        self._reserves[realm] = self._reserves.get(realm, 0.0) + amount
        return self._reserves[realm]

    def issue_credit(self, realm: str, amount: float) -> bool:
        total_reserves = sum(self._reserves.values())
        total_credit = sum(self._credit_outstanding.values())
        if (total_credit + amount) > total_reserves / self.reserve_ratio:
            return False
        self._credit_outstanding[realm] = self._credit_outstanding.get(realm, 0.0) + amount
        return True

    def repay(self, realm: str, amount: float) -> None:
        prev = self._credit_outstanding.get(realm, 0.0)
        self._credit_outstanding[realm] = max(0.0, prev - amount)

    def default(self, realm: str) -> None:
        if self._credit_outstanding.get(realm, 0.0) > 0:
            self._defaults += 1
            self._credit_outstanding[realm] = 0.0
            self._reserves[realm] = max(0.0, self._reserves.get(realm, 0.0) - 10.0)

    def stability_ratio(self) -> float:
        total_reserves = sum(self._reserves.values())
        total_credit = sum(self._credit_outstanding.values())
        if total_credit == 0:
            return 1.0
        return round(total_reserves / (total_credit * self.reserve_ratio), 4)

    def status(self) -> Dict[str, Any]:
        return {"realms": len(self._reserves),
                "total_reserves": round(sum(self._reserves.values()), 4),
                "credit_outstanding": round(sum(self._credit_outstanding.values()), 4),
                "stability_ratio": self.stability_ratio(),
                "defaults": self._defaults}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    bank = AllianceBank()
    return {"status": "active", "module": "alliance_bank",
            **bank.status()}
