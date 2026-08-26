"""Wave 127 — Gravitational Pricing (Enhanced).

Pricing based on gravitational pull — modules with more connections,
usage, and importance have stronger gravitational fields and thus
higher prices, creating a natural economic hierarchy.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class GravitationalItem:
    """An item priced by gravitational pull."""

    def __init__(self, name: str, base_price: float = 1.0):
        self.name = name
        self.base_price = base_price
        self.connections = 0
        self.usage_count = 0
        self.created = time.time()

    @property
    def mass(self) -> float:
        return self.connections * 0.3 + self.usage_count * 0.1 + 1.0

    @property
    def price(self) -> float:
        return self.base_price * (1 + self.mass * 0.1)

    def add_connection(self) -> None:
        self.connections += 1

    def use(self) -> None:
        self.usage_count += 1

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "mass": round(self.mass, 4),
                "price": round(self.price, 4), "connections": self.connections,
                "usage": self.usage_count}


class GravitationalPricingEngine:
    """Dynamic pricing based on gravitational pull."""

    def __init__(self):
        self._items: Dict[str, GravitationalItem] = {}

    def add_item(self, name: str, base_price: float = 1.0) -> GravitationalItem:
        item = GravitationalItem(name, base_price)
        self._items[name] = item
        return item

    def purchase(self, name: str, buyer: str) -> Dict[str, Any]:
        item = self._items.get(name)
        if not item:
            return {"error": "item not found"}
        item.use()
        return {"buyer": buyer, "item": name, "price": round(item.price, 4),
                "mass": round(item.mass, 4)}

    def connect_items(self, name_a: str, name_b: str) -> bool:
        a, b = self._items.get(name_a), self._items.get(name_b)
        if a and b:
            a.add_connection()
            b.add_connection()
            return True
        return False

    def price_list(self) -> List[Dict[str, Any]]:
        return [i.to_dict() for i in sorted(self._items.values(), key=lambda x: x.price, reverse=True)]

    def status(self) -> Dict[str, Any]:
        return {"total_items": len(self._items),
                "total_value": round(sum(i.price for i in self._items.values()), 4)}
