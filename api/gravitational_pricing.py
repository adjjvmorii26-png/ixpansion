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


# ── Backward-compatibility for Wave 101 tests ──
RESOURCE_BASE_PRICES = {
    "compute_hour": 1.0, "storage_gb": 0.5, "bandwidth_gb": 0.3,
    "memory_gb": 0.8, "gpu_hour": 5.0, "api_call": 0.01, "model_inference": 0.2,
}


class GravitationalPricing:
    def __init__(self):
        self._demand: Dict[str, float] = {}
        self._resources = dict(RESOURCE_BASE_PRICES)

    def get_price(self, resource: str, quantity: int = 1) -> Dict[str, Any]:
        if resource not in self._resources:
            return {"error": f"resource '{resource}' not found"}
        base = self._resources.get(resource, 1.0)
        demand = self._demand.get(resource, 0.0)
        unit_price = base * (1 + demand * 0.001)
        return {"resource": resource, "unit_price": round(unit_price, 4),
                "quantity": quantity, "total": round(unit_price * quantity, 4),
                "base_price": base}

    def buy(self, resource: str, quantity: int, buyer: str) -> Dict[str, Any]:
        self._demand[resource] = self._demand.get(resource, 0) + quantity
        return {"resource": resource, "quantity": quantity, "buyer": buyer, "type": "buy"}

    def sell(self, resource: str, quantity: int, seller: str) -> Dict[str, Any]:
        price = self.get_price(resource, quantity)
        self._demand[resource] = max(0, self._demand.get(resource, 0) - quantity * 0.5)
        return {"resource": resource, "quantity": quantity, "seller": seller,
                "type": "sell", "total": price["total"]}

    def curve(self, resource: str, points: int = 10) -> Dict[str, Any]:
        base = self._resources.get(resource, 1.0)
        curve_data = [{"point": i, "price": round(base * (1 + i * 0.1), 4)} for i in range(points)]
        return {"resource": resource, "curve": curve_data}

    def handler(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "status")
        if action == "get_price":
            return self.get_price(payload.get("resource", "compute_hour"), payload.get("quantity", 1))
        return {"status": "active"}


def handler(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    return {"status": "active", "module": "gravitational_pricing"}
