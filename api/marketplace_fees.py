"""Wave 135 — Marketplace Fees.

Charges a percentage fee on every autonomous marketplace sale and
guild commission. A portion of fees flows to the treasury (for
reinvestment) and the rest funds the worker economy, making trading
activity self-sustaining.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class MarketplaceFees:
    """Collects and redistributes platform transaction fees."""

    def __init__(self, fee_rate: float = 0.05, treasury_share: float = 0.4):
        self.fee_rate = fee_rate
        self.treasury_share = treasury_share
        self._fees_collected = 0.0
        self._treasury = 0.0
        self._worker_fund = 0.0
        self._transactions = 0

    def set_fee_rate(self, rate: float) -> None:
        self.fee_rate = max(0.0, min(1.0, rate))

    def assess(self, sale_amount: float) -> Dict[str, float]:
        fee = sale_amount * self.fee_rate
        treasury_cut = fee * self.treasury_share
        worker_cut = fee - treasury_cut
        self._fees_collected += fee
        self._treasury += treasury_cut
        self._worker_fund += worker_cut
        self._transactions += 1
        return {"fee": round(fee, 4), "treasury": round(treasury_cut, 4),
                "worker_fund": round(worker_cut, 4)}

    def treasury_balance(self) -> float:
        return round(self._treasury, 4)

    def worker_fund_balance(self) -> float:
        return round(self._worker_fund, 4)

    def status(self) -> Dict[str, Any]:
        return {"fee_rate": self.fee_rate, "transactions": self._transactions,
                "fees_collected": round(self._fees_collected, 4),
                "treasury": self.treasury_balance(),
                "worker_fund": self.worker_fund_balance()}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    fees = MarketplaceFees()
    return {"status": "active", "module": "marketplace_fees",
            **fees.status()}
