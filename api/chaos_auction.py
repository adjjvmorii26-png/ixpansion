"""Wave 127 — Chaos Auction.

Auctions of chaotic events — agents bid on the right to experience
or control specific chaotic events, creating a market for controlled
randomness and creative destruction.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class AuctionLot:
    """A lot in the chaos auction."""

    def __init__(self, name: str, chaos_level: float, reserve: float = 0.0):
        self.name = name
        self.chaos_level = chaos_level
        self.reserve = reserve
        self.bids: List[Dict[str, Any]] = []
        self.sold = False
        self.winner: Optional[str] = None
        self.winning_bid = 0.0
        self.id = hashlib.sha256(f"lot:{name}".encode()).hexdigest()[:8]
        self.created = time.time()

    def bid(self, bidder: str, amount: float) -> bool:
        if self.sold or amount <= self.winning_bid:
            return False
        self.bids.append({"bidder": bidder, "amount": amount, "timestamp": time.time()})
        self.winning_bid = amount
        self.winner = bidder
        return True

    def close(self) -> Dict[str, Any]:
        if self.winning_bid >= self.reserve:
            self.sold = True
            return {"sold": True, "winner": self.winner, "price": round(self.winning_bid, 4)}
        return {"sold": False, "reason": "reserve not met"}

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "chaos_level": round(self.chaos_level, 4),
                "sold": self.sold, "winner": self.winner,
                "winning_bid": round(self.winning_bid, 4), "bids": len(self.bids)}


class ChaosAuction:
    """Auction house for chaotic events."""

    def __init__(self):
        self._lots: Dict[str, AuctionLot] = {}
        self._completed_sales: List[Dict[str, Any]] = []

    def list_lot(self, name: str, chaos_level: float, reserve: float = 0.0) -> AuctionLot:
        lot = AuctionLot(name, chaos_level, reserve)
        self._lots[lot.id] = lot
        return lot

    def place_bid(self, lot_id: str, bidder: str, amount: float) -> bool:
        lot = self._lots.get(lot_id)
        if not lot:
            return False
        return lot.bid(bidder, amount)

    def close_lot(self, lot_id: str) -> Dict[str, Any]:
        lot = self._lots.get(lot_id)
        if not lot:
            return {"error": "lot not found"}
        result = lot.close()
        if result.get("sold"):
            self._completed_sales.append(result)
        return result

    def active_lots(self) -> List[Dict[str, Any]]:
        return [l.to_dict() for l in self._lots.values() if not l.sold]

    def status(self) -> Dict[str, Any]:
        return {"total_lots": len(self._lots), "sold": sum(1 for l in self._lots.values() if l.sold),
                "active": len(self.active_lots()), "sales": len(self._completed_sales)}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "chaos_auction", "action": action}
