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



# Backward-compatibility for Wave 102 tests
class TemporalArbitrage:
    def __init__(self):
        self._bridges: Dict[str, Dict[str, Any]] = {}
        self._history: List[Dict[str, Any]] = []

    def setup(self, resource: str, trader: str, low: float, high: float) -> Dict[str, Any]:
        import hashlib as _hl
        bid = _hl.sha256(f"{resource}:{trader}".encode()).hexdigest()[:8]
        self._bridges[bid] = {"resource": resource, "trader": trader,
                               "low": low, "high": high}
        return {"bridge_id": bid, "resource": resource, "low": low, "high": high}

    def execute(self, bridge_id: str, current_price: float = 0.0) -> Dict[str, Any]:
        bridge = self._bridges.get(bridge_id)
        if not bridge:
            return {"error": "bridge not found"}
        action = "buy" if current_price <= bridge["low"] else "sell" if current_price >= bridge["high"] else "hold"
        profit = 0.0
        if action == "buy":
            profit = bridge["low"] - current_price
        elif action == "sell":
            profit = current_price - bridge["high"]
        result = {"bridge_id": bridge_id, "action": action, "price": current_price,
                  "profit": round(max(0.0, profit), 4), "trader": bridge["trader"]}
        self._history.append(result)
        return result

    def opportunities(self) -> List[Dict[str, Any]]:
        return [{"bridge_id": bid, "resource": b["resource"],
                 "low": b["low"], "high": b["high"]} for bid, b in self._bridges.items()]

    def history_log(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._history[-limit:]

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def handler(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "active", "bridges": len(self._bridges)}

def handler(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    return {"status": "active", "module": "temporal_arbitrage"}
