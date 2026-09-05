"""Wave 127 — Entropy Exchange.

A marketplace where entropy (chaos) and negentropy (order) are traded
as commodities. Modules buy order when they need stability and sell
order when they have excess, creating a self-balancing economy of chaos.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class EntropyCommodity:
    """A commodity on the entropy exchange."""

    def __init__(self, name: str, entropy_level: float):
        self.name = name
        self.entropy_level = entropy_level
        self.price = entropy_level * 10.0
        self.created = time.time()
        self.history: List[Dict[str, Any]] = []

    @property
    def commodity_type(self) -> str:
        return "chaos" if self.entropy_level > 0.5 else "order"

    def update_price(self, delta: float) -> float:
        self.price = max(0.1, self.price + delta)
        self.history.append({"price": round(self.price, 4), "timestamp": time.time()})
        return self.price

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "entropy": round(self.entropy_level, 4),
                "type": self.commodity_type, "price": round(self.price, 4),
                "history": len(self.history)}


class EntropyExchange:
    """Marketplace for trading entropy and order."""

    def __init__(self):
        self._commodities: Dict[str, EntropyCommodity] = {}
        self._trades: List[Dict[str, Any]] = []
        self._balance_sheet: Dict[str, float] = {}

    def list_commodity(self, name: str, entropy: float) -> EntropyCommodity:
        commodity = EntropyCommodity(name, entropy)
        self._commodities[name] = commodity
        return commodity

    def trade(self, buyer: str, seller: str, commodity_name: str) -> Dict[str, Any]:
        commodity = self._commodities.get(commodity_name)
        if not commodity:
            return {"error": "commodity not found"}
        price = commodity.price
        self._balance_sheet[buyer] = self._balance_sheet.get(buyer, 0) - price
        self._balance_sheet[seller] = self._balance_sheet.get(seller, 0) + price
        trade = {"buyer": buyer, "seller": seller, "commodity": commodity_name,
                 "price": round(price, 4), "type": commodity.commodity_type,
                 "timestamp": time.time()}
        self._trades.append(trade)
        commodity.update_price(0.5)
        return trade

    def market_value(self) -> float:
        return sum(c.price for c in self._commodities.values())

    def get_balance(self, agent: str) -> float:
        return self._balance_sheet.get(agent, 0.0)

    def status(self) -> Dict[str, Any]:
        chaos = sum(1 for c in self._commodities.values() if c.commodity_type == "chaos")
        order = sum(1 for c in self._commodities.values() if c.commodity_type == "order")
        return {"commodities": len(self._commodities), "trades": len(self._trades),
                "market_value": round(self.market_value(), 4),
                "chaos_items": chaos, "order_items": order}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "entropy_exchange", "action": action}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "127", "module": "entropy_exchange"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
