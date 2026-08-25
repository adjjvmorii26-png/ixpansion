"""Gravitational Pricing — dynamic pricing that responds to demand like gravity.

Prices are not fixed. They warp based on demand density, creating
gravity wells of value. High demand pulls prices up exponentially.
Low demand lets prices fall into valleys. Users learn to buy in
valleys and sell at peaks.

Usage:
    POST /api/gravity/price         — get current price for a resource
    POST /api/gravity/buy           — purchase at gravitational price
    POST /api/gravity/sell          — sell back at gravitational price
    GET  /api/gravity/curve         — view the pricing curve
    GET  /api/gravity/history       — price history
"""
from __future__ import annotations

import hashlib
import json
import math
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RESOURCE_BASE_PRICES = {
    "compute_hour": 1.0,
    "storage_gb": 0.10,
    "bandwidth_gb": 0.05,
    "agent_cycle": 0.50,
    "quantum_shot": 0.01,
    "dream_output": 2.0,
    "entropy_unit": 0.25,
    "memory_slot": 0.15,
}

GRAVITY_CONSTANT = 0.001  # How strongly demand affects price
MAX_WARP = 10.0  # Maximum price multiplier
MIN_WARP = 0.1   # Minimum price multiplier (deep valley)


def _gravitational_warp(base_price: float, demand: float, supply: float) -> float:
    """Compute price warp from demand/supply ratio."""
    ratio = demand / max(supply, 1)
    warp = 1.0 + (GRAVITY_CONSTANT * ratio ** 2)
    warp = max(MIN_WARP, min(MAX_WARP, warp))
    return round(base_price * warp, 6)


class GravitationalPricing:
    def __init__(self):
        self.demand_history: Dict[str, List[Dict]] = {}
        self.transactions: List[Dict] = {}
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "gravity_pricing.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.demand_history = data.get("demand_history", {})
            self.transactions = data.get("transactions", {})

    def _save(self):
        path = ROOT / ".runtime" / "gravity_pricing.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "demand_history": {k: v[-200:] for k, v in self.demand_history.items()},
            "transactions": {k: v[-200:] for k, v in self.transactions.items()},
        }, indent=2))

    def get_price(self, resource: str, quantity: int = 1) -> Dict:
        if resource not in RESOURCE_BASE_PRICES:
            return {"error": f"unknown resource: {resource}"}
        base = RESOURCE_BASE_PRICES[resource]
        history = self.demand_history.get(resource, [])
        recent_demand = sum(h["quantity"] for h in history[-20:]) if history else 0
        recent_supply = max(100 - recent_demand, 1)
        unit_price = _gravitational_warp(base, recent_demand, recent_supply)
        total = round(unit_price * quantity, 6)
        warp_factor = round(unit_price / base, 4)
        return {
            "resource": resource,
            "quantity": quantity,
            "base_price": base,
            "unit_price": unit_price,
            "total": total,
            "warp_factor": warp_factor,
            "demand_pressure": "high" if warp_factor > 2 else "moderate" if warp_factor > 1.2 else "low",
        }

    def buy(self, resource: str, quantity: int, buyer: str) -> Dict:
        price_info = self.get_price(resource, quantity)
        if "error" in price_info:
            return price_info
        tx_id = hashlib.sha256(f"{buyer}:{resource}:{time.time()}".encode()).hexdigest()[:10]
        tx = {
            "tx_id": tx_id, "type": "buy", "resource": resource,
            "quantity": quantity, "price": price_info["unit_price"],
            "total": price_info["total"], "buyer": buyer,
            "timestamp": time.time(),
        }
        if resource not in self.transactions:
            self.transactions[resource] = []
        self.transactions[resource].append(tx)
        if resource not in self.demand_history:
            self.demand_history[resource] = []
        self.demand_history[resource].append({"quantity": quantity, "timestamp": time.time()})
        self._save()
        return tx

    def sell(self, resource: str, quantity: int, seller: str) -> Dict:
        price_info = self.get_price(resource, quantity)
        if "error" in price_info:
            return price_info
        sale_price = round(price_info["unit_price"] * 0.95, 6)  # 5% spread
        tx_id = hashlib.sha256(f"{seller}:sell:{resource}:{time.time()}".encode()).hexdigest()[:10]
        tx = {
            "tx_id": tx_id, "type": "sell", "resource": resource,
            "quantity": quantity, "price": sale_price,
            "total": round(sale_price * quantity, 6), "seller": seller,
            "timestamp": time.time(),
        }
        if resource not in self.transactions:
            self.transactions[resource] = []
        self.transactions[resource].append(tx)
        self._save()
        return tx

    def curve(self, resource: str, points: int = 20) -> Dict:
        if resource not in RESOURCE_BASE_PRICES:
            return {"error": f"unknown resource: {resource}"}
        base = RESOURCE_BASE_PRICES[resource]
        curve_points = []
        for i in range(points):
            demand = i * 5
            supply = max(100 - demand, 1)
            price = _gravitational_warp(base, demand, supply)
            curve_points.append({"demand": demand, "price": price})
        return {"resource": resource, "base_price": base, "curve": curve_points}

    def history(self, resource: str, limit: int = 20) -> List[Dict]:
        return self.transactions.get(resource, [])[-limit:]


def handler(request, response):
    gp = GravitationalPricing()
    return {"resources": list(RESOURCE_BASE_PRICES.keys())}


def demo():
    gp = GravitationalPricing()
    print("=== Gravitational Pricing ===")
    for res in ["compute_hour", "dream_output", "entropy_unit"]:
        p = gp.get_price(res)
        print(f"\n{res}: base=${p['base_price']}, current=${p['unit_price']} ({p['demand_pressure']})")
        gp.buy(res, 10, "user_1")
        gp.buy(res, 20, "user_2")
        p2 = gp.get_price(res)
        print(f"  After demand: ${p2['unit_price']} (warp: {p2['warp_factor']}x)")

    curve = gp.curve("compute_hour")
    print(f"\nCurve for compute_hour: {len(curve['curve'])} points")
    return {"resources": len(RESOURCE_BASE_PRICES)}


if __name__ == "__main__":
    demo()
