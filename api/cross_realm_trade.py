"""Wave 138 — Cross-Realm Trade.

The commercial channel between the civilization and allied realms.
Difference in resource abundance enables arbitrage; trade lanes have
a transit cost and risk. The engine clears trades and balances the
two realms' ledgers.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class CrossRealmTrade:
    """Facilitates and tracks commerce between realms."""

    def __init__(self, lane_cost: float = 0.05):
        self.lane_cost = lane_cost
        self._trades: List[Dict[str, Any]] = []
        self._volume = 0.0
        self._cleared = 0

    def execute(self, realm_a: str, realm_b: str, commodity: str,
                quantity: float, local_price: float, foreign_price: float) -> Dict[str, Any]:
        """Clears a trade if arbitrage + lane cost is profitable."""
        margin = foreign_price - local_price
        net = margin * quantity - self.lane_cost * (local_price * quantity)
        profitable = net > 0
        trade = {
            "commodity": commodity, "quantity": quantity,
            "realms": [realm_a, realm_b], "margin": round(net, 4),
            "profitable": profitable,
            "id": hashlib.sha256(f"trade:{commodity}:{realm_a}".encode()).hexdigest()[:10],
        }
        self._trades.append(trade)
        if profitable:
            self._volume += net
            self._cleared += 1
        return trade

    def profit_arbitrage_opportunities(self) -> List[Dict[str, Any]]:
        return [t for t in self._trades if t["profitable"]]

    def status(self) -> Dict[str, Any]:
        return {"trades": len(self._trades), "cleared": self._cleared,
                "net_volume": round(self._volume, 4),
                "lane_cost": self.lane_cost}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    trade = CrossRealmTrade()
    return {"status": "active", "module": "cross_realm_trade",
            **trade.status()}
