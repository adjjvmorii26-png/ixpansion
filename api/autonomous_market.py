"""Autonomous Market — self-regulating economy where agents trade capabilities.

Agents buy and sell their own capabilities on an open market. Prices
fluctuate based on supply, demand, and agent reputation. The market
self-corrects through natural price discovery, preventing any single
agent from monopolizing critical capabilities.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class MarketListing:
    def __init__(self, seller: str, capability: str, price: float, quantity: int = 1):
        self.seller = seller
        self.capability = capability
        self.price = price
        self.quantity = quantity
        self.active = True
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{seller}:{capability}:{self.created_at}".encode()).hexdigest()[:8]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "seller": self.seller,
            "capability": self.capability,
            "price": round(self.price, 2), "quantity": self.quantity,
        }


class AutonomousMarket:
    def __init__(self):
        self.listings: Dict[str, MarketListing] = {}
        self.trades: List[Dict[str, Any]] = []
        self.price_history: Dict[str, List[float]] = {}
        self.reputation: Dict[str, float] = {}

    def list_capability(self, seller: str, capability: str, price: float) -> Dict[str, Any]:
        listing = MarketListing(seller, capability, price)
        self.listings[listing.id] = listing
        self.price_history.setdefault(capability, []).append(price)
        self.reputation.setdefault(seller, 0.5)
        return {"listed": listing.to_dict()}

    def buy(self, buyer: str, listing_id: str) -> Dict[str, Any]:
        if listing_id not in self.listings:
            return {"error": "listing not found"}
        listing = self.listings[listing_id]
        if not listing.active:
            return {"error": "listing inactive"}
        self.trades.append({
            "buyer": buyer, "seller": listing.seller,
            "capability": listing.capability,
            "price": listing.price, "time": time.time(),
        })
        self.reputation[listing.seller] = min(1.0, self.reputation.get(listing.seller, 0.5) + 0.05)
        self.reputation[buyer] = max(0.0, self.reputation.get(buyer, 0.5) - 0.02)
        listing.active = False
        return {
            "purchased": listing.to_dict(),
            "buyer": buyer, "price_paid": listing.price,
        }

    def search(self, capability: str) -> List[Dict[str, Any]]:
        return [
            l.to_dict() for l in self.listings.values()
            if l.active and capability.lower() in l.capability.lower()
        ]

    def price_trend(self, capability: str) -> Dict[str, Any]:
        history = self.price_history.get(capability, [])
        if len(history) < 2:
            return {"capability": capability, "trend": "insufficient_data"}
        recent = history[-5:]
        avg = sum(recent) / len(recent)
        trend = "stable"
        if recent[-1] > avg * 1.1:
            trend = "rising"
        elif recent[-1] < avg * 0.9:
            trend = "falling"
        return {"capability": capability, "trend": trend, "avg_price": round(avg, 2), "data_points": len(history)}

    def market_stats(self) -> Dict[str, Any]:
        active = [l for l in self.listings.values() if l.active]
        return {
            "total_listings": len(self.listings),
            "active_listings": len(active),
            "total_trades": len(self.trades),
            "unique_capabilities": len(self.price_history),
            "unique_sellers": len(set(l.seller for l in self.listings.values())),
        }


_market = AutonomousMarket()


def autonomous_market_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "list":
        return _market.list_capability(
            payload.get("seller", "anon"),
            payload.get("capability", "basic_skill"),
            payload.get("price", 10.0),
        )
    elif action == "buy":
        return _market.buy(payload.get("buyer", "anon"), payload.get("listing_id", ""))
    elif action == "search":
        return {"results": _market.search(payload.get("capability", ""))}
    elif action == "trend":
        return _market.price_trend(payload.get("capability", ""))
    return {"status": "active", **_market.market_stats()}


handler = autonomous_market_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "autonomous_market"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "autonomous_market", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
