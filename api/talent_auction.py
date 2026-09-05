"""Talent Auction — agents bid on each other's time and capabilities.

Specialized agents auction their skills to the highest bidder. The auction
creates a natural marketplace for expertise, where rare skills command
premium prices and common skills remain affordable.
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


class Auction:
    def __init__(self, seller: str, skill: str, base_price: float, duration_ticks: int = 10):
        self.seller = seller
        self.skill = skill
        self.base_price = base_price
        self.current_price = base_price
        self.duration = duration_ticks
        self.tick = 0
        self.bids: List[Dict[str, Any]] = []
        self.winner: str = ""
        self.completed = False
        self.id = hashlib.sha256(f"{seller}:{skill}:{time.time()}".encode()).hexdigest()[:8]

    def bid(self, bidder: str, amount: float) -> Dict[str, Any]:
        if self.completed:
            return {"error": "auction ended"}
        if amount <= self.current_price:
            return {"error": "bid too low"}
        self.bids.append({"bidder": bidder, "amount": amount, "tick": self.tick})
        self.current_price = amount
        return {"accepted": True, "current_price": round(amount, 2)}

    def advance_tick(self) -> Dict[str, Any]:
        if self.completed:
            return {"status": "completed"}
        self.tick += 1
        if self.tick >= self.duration:
            self.completed = True
            if self.bids:
                best = max(self.bids, key=lambda b: b["amount"])
                self.winner = best["bidder"]
            return {"status": "completed", "winner": self.winner, "price": self.current_price}
        return {"status": "active", "tick": self.tick, "current_price": self.current_price}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "seller": self.seller,
            "skill": self.skill,
            "base_price": self.base_price,
            "current_price": round(self.current_price, 2),
            "bids": len(self.bids),
            "completed": self.completed,
            "winner": self.winner,
        }


class TalentAuction:
    def __init__(self):
        self.auctions: Dict[str, Auction] = []
        self.completed_sales: List[Dict[str, Any]] = []

    def list_auction(self, seller: str, skill: str, base_price: float) -> Dict[str, Any]:
        auction = Auction(seller, skill, base_price)
        self.auctions.append(auction)
        return {"listed": auction.to_dict()}

    def place_bid(self, auction_id: str, bidder: str, amount: float) -> Dict[str, Any]:
        for auction in self.auctions:
            if auction.id == auction_id:
                return auction.bid(bidder, amount)
        return {"error": "auction not found"}

    def advance_all(self) -> List[Dict[str, Any]]:
        results = []
        for auction in self.auctions:
            result = auction.advance_tick()
            if result.get("status") == "completed" and result.get("winner"):
                self.completed_sales.append({
                    "seller": auction.seller,
                    "buyer": result["winner"],
                    "skill": auction.skill,
                    "price": result["price"],
                })
            results.append({"auction_id": auction.id, **result})
        return results

    def active_auctions(self) -> List[Dict[str, Any]]:
        return [a.to_dict() for a in self.auctions if not a.completed]

    def auction_stats(self) -> Dict[str, Any]:
        return {
            "total_auctions": len(self.auctions),
            "active": sum(1 for a in self.auctions if not a.completed),
            "completed": sum(1 for a in self.auctions if a.completed),
            "total_sales": len(self.completed_sales),
            "total_revenue": round(sum(s["price"] for s in self.completed_sales), 2),
        }


_auction = TalentAuction()


def talent_auction_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "list":
        return _auction.list_auction(
            payload.get("seller", "expert"),
            payload.get("skill", "analysis"),
            payload.get("base_price", 10.0),
        )
    elif action == "bid":
        return _auction.place_bid(
            payload.get("auction_id", ""),
            payload.get("bidder", "buyer"),
            payload.get("amount", 0.0),
        )
    elif action == "advance":
        return {"results": _auction.advance_all()}
    elif action == "active":
        return {"auctions": _auction.active_auctions()}
    return {"status": "active", **_auction.auction_stats()}


handler = talent_auction_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "talent_auction"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "talent_auction", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
