"""Wave 127 — Temporal Arbitrage.

Exploits time-dependent price differences across the system — buying
order when it's cheap (during calm periods) and selling during chaos
when order is scarce and valuable.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class ArbitrageOpportunity:
    """A detected price difference across time."""

    def __init__(self, item: str, buy_time: float, sell_time: float, spread: float):
        self.item = item
        self.buy_time = buy_time
        self.sell_time = sell_time
        self.spread = spread
        self.executed = False
        self.profit = 0.0

    def execute(self) -> Dict[str, Any]:
        self.executed = True
        self.profit = self.spread
        return {"item": self.item, "spread": round(self.spread, 4),
                "profit": round(self.profit, 4), "executed": True}

    def to_dict(self) -> Dict[str, Any]:
        return {"item": self.item, "spread": round(self.spread, 4),
                "executed": self.executed, "profit": round(self.profit, 4)}


class TemporalArbitrageEngine:
    """Detects and exploits temporal price differences."""

    def __init__(self):
        self._opportunities: List[ArbitrageOpportunity] = []
        self._price_history: Dict[str, List[float]] = {}
        self._total_profit = 0.0

    def record_price(self, item: str, price: float) -> None:
        self._price_history.setdefault(item, []).append(price)

    def detect(self, item: str, threshold: float = 0.5) -> Dict[str, Any]:
        prices = self._price_history.get(item, [])
        if len(prices) < 2:
            return {"detected": False}
        min_price = min(prices)
        max_price = max(prices)
        spread = max_price - min_price
        if spread > threshold:
            opp = ArbitrageOpportunity(item, time.time(), time.time(), spread)
            self._opportunities.append(opp)
            return {"detected": True, "spread": round(spread, 4), "item": item}
        return {"detected": False, "spread": round(spread, 4)}

    def execute(self, opportunity_index: int) -> Dict[str, Any]:
        if 0 <= opportunity_index < len(self._opportunities):
            opp = self._opportunities[opportunity_index]
            result = opp.execute()
            self._total_profit += result["profit"]
            return result
        return {"error": "opportunity not found"}

    def status(self) -> Dict[str, Any]:
        executed = sum(1 for o in self._opportunities if o.executed)
        return {"opportunities": len(self._opportunities), "executed": executed,
                "total_profit": round(self._total_profit, 4)}
