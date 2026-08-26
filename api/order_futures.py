"""Wave 127 — Order Futures.

Futures contracts on future system order — agents can buy promises of
future stability, hedging against chaotic events, or speculate on
increasing order in the system.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class OrderFuture:
    """A futures contract on future system order."""

    def __init__(self, name: str, predicted_order: float, expiry_ticks: int = 10):
        self.name = name
        self.predicted_order = predicted_order
        self.expiry_ticks = expiry_ticks
        self.ticks_remaining = expiry_ticks
        self.price = predicted_order * 100.0
        self.owner: Optional[str] = None
        self.settled = False
        self.id = hashlib.sha256(f"future:{name}".encode()).hexdigest()[:8]

    def tick(self) -> float:
        if self.ticks_remaining > 0:
            self.ticks_remaining -= 1
        self.price = max(0.0, self.price - 0.5)
        return self.price

    def settle(self, actual_order: float) -> Dict[str, Any]:
        profit = (actual_order - self.predicted_order) * 100.0
        self.settled = True
        return {"name": self.name, "predicted": self.predicted_order,
                "actual": actual_order, "profit": round(profit, 4),
                "settled": True}

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "price": round(self.price, 4),
                "ticks_remaining": self.ticks_remaining, "settled": self.settled}


class OrderFuturesMarket:
    """Market for futures on future system order."""

    def __init__(self):
        self._futures: Dict[str, OrderFuture] = {}
        self._settled: List[Dict[str, Any]] = []
        self._tick_count = 0

    def create_future(self, name: str, predicted_order: float, expiry: int = 10) -> OrderFuture:
        future = OrderFuture(name, predicted_order, expiry)
        self._futures[future.id] = future
        return future

    def buy(self, future_id: str, buyer: str) -> Dict[str, Any]:
        future = self._futures.get(future_id)
        if not future or future.settled:
            return {"error": "future not available"}
        future.owner = buyer
        return {"buyer": buyer, "price": round(future.price, 4), "future": future.name}

    def tick(self) -> int:
        self._tick_count += 1
        active = 0
        for f in self._futures.values():
            if not f.settled:
                f.tick()
                active += 1
        return active

    def status(self) -> Dict[str, Any]:
        active = sum(1 for f in self._futures.values() if not f.settled)
        return {"total_futures": len(self._futures), "active": active,
                "settled": len(self._settled), "ticks": self._tick_count}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "order_futures", "action": action}
