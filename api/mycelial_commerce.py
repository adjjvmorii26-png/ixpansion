"""Mycelial Commerce — marketplace where listings grow like mycelium.

Products don't sit on shelves. They spread, connect, and form networks.
A listing for "quantum analysis" might sprout connections to "entropy
forecasting" and "pattern detection." Prices are determined by network
position and connectivity.

Usage:
    POST /api/mycelium/list        — create a listing
    POST /api/mycelium/connect     — connect two listings
    POST /api/mycelium/grow        — trigger growth
    GET  /api/mycelium/network     — view the mycelial network
    GET  /api/mycelium/prices      — connectivity-based pricing
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _connectivity_price(base_price: float, connections: int, depth: int) -> float:
    """Price increases with network connectivity (metabolic cost)."""
    network_bonus = math.log2(connections + 1) * 0.5
    depth_bonus = depth * 0.1
    return round(base_price * (1 + network_bonus + depth_bonus), 2)


class MycelialCommerce:
    def __init__(self):
        self.listings: Dict[str, Dict] = {}
        self.connections: List[Dict] = []
        self.growth_events: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "mycelial.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            return  # read-only fs (serverless)
        if path.exists():
            data = json.loads(path.read_text())
            self.listings = data.get("listings", {})
            self.connections = data.get("connections", [])
            self.growth_events = data.get("growth_events", [])

    def _save(self):
        try:
            path = ROOT / ".runtime" / "mycelial.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({
                "listings": self.listings,
                "connections": self.connections[-1000:],
                "growth_events": self.growth_events[-500:],
            }, indent=2))
        except OSError:
            pass  # read-only fs (serverless)

    def list_item(self, seller: str, name: str, description: str,
                  base_price: float, category: str = "general") -> Dict:
        listing_id = hashlib.sha256(f"{seller}:{name}:{time.time()}".encode()).hexdigest()[:10]
        self.listings[listing_id] = {
            "name": name, "description": description,
            "base_price": base_price, "seller": seller,
            "category": category, "connections": 0,
            "depth": 0, "health": 1.0,
            "mycelia": [], "offspring": [],
            "created": time.time(),
        }
        self._save()
        return {"listing_id": listing_id, "name": name}

    def connect(self, listing_a: str, listing_b: str, relationship: str = "symbiotic") -> Dict:
        if listing_a not in self.listings or listing_b not in self.listings:
            return {"error": "listing not found"}
        if listing_a == listing_b:
            return {"error": "cannot connect to self"}
        conn = {
            "from": listing_a, "to": listing_b,
            "relationship": relationship,
            "strength": round(random.uniform(0.3, 1.0), 3),
            "created": time.time(),
        }
        self.connections.append(conn)
        self.listings[listing_a]["connections"] += 1
        self.listings[listing_b]["connections"] += 1
        self.listings[listing_a]["mycelia"].append(listing_b)
        self.listings[listing_b]["mycelia"].append(listing_a)
        self._save()
        return {"connected": True, "relationship": relationship, "strength": conn["strength"]}

    def grow(self, listing_id: str) -> Dict:
        if listing_id not in self.listings:
            return {"error": "listing not found"}
        listing = self.listings[listing_id]
        old_depth = listing["depth"]
        listing["depth"] += 1
        listing["connections"] += random.randint(1, 3)
        listing["health"] = min(1.0, listing["health"] + 0.1)
        growth = {
            "listing_id": listing_id,
            "old_depth": old_depth,
            "new_depth": listing["depth"],
            "new_connections": listing["connections"],
            "timestamp": time.time(),
        }
        self.growth_events.append(growth)
        self._save()
        return growth

    def network(self) -> Dict:
        nodes = []
        for lid, listing in self.listings.items():
            nodes.append({
                "id": lid,
                "name": listing["name"],
                "connections": listing["connections"],
                "depth": listing["depth"],
                "health": listing["health"],
            })
        return {"nodes": nodes, "edges": len(self.connections), "total_listings": len(self.listings)}

    def prices(self) -> List[Dict]:
        result = []
        for lid, listing in self.listings.items():
            price = _connectivity_price(listing["base_price"], listing["connections"], listing["depth"])
            result.append({
                "listing_id": lid,
                "name": listing["name"],
                "base_price": listing["base_price"],
                "current_price": price,
                "connections": listing["connections"],
                "depth": listing["depth"],
            })
        return result


def handler(request, response):
    mc = MycelialCommerce()
    net = mc.network()
    return {"total_listings": net["total_listings"], "total_edges": net["edges"]}


def demo():
    mc = MycelialCommerce()
    print("=== Mycelial Commerce ===")
    a = mc.list_item("seller_1", "Quantum Analysis", "Deep quantum pattern analysis", 10.0, "analysis")
    b = mc.list_item("seller_2", "Entropy Forecast", "Predict entropy trends", 8.0, "forecasting")
    c = mc.list_item("seller_3", "Pattern Weaving", "Cross-system pattern synthesis", 15.0, "synthesis")

    mc.connect(a["listing_id"], b["listing_id"], "complementary")
    mc.connect(a["listing_id"], c["listing_id"], "symbiotic")
    mc.connect(b["listing_id"], c["listing_id"], "competitive")

    mc.grow(a["listing_id"])
    mc.grow(a["listing_id"])

    prices = mc.prices()
    for p in prices:
        print(f"  {p['name']}: base=${p['base_price']}, current=${p['current_price']} (depth={p['depth']})")

    net = mc.network()
    print(f"\nNetwork: {net['total_listings']} nodes, {net['edges']} edges")
    return net


if __name__ == "__main__":
    demo()


def coherence_vitals() -> dict:
    """mycelial_commerce reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "mycelial_commerce_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['neural_fabric', 'plugin_loader', 'pattern_recognizer']

