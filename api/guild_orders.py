"""Wave 134 — Guild Orders.

External clients commission orders that are routed to the guild with
the best craft match. Orders progress through quoting, acceptance,
fulfillment, and review — turning the workforce civilization into a
service provider with a reputation-rated storefront.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class Order:
    """A commissioned order fulfilled by the guild system."""

    def __init__(self, client: str, title: str, craft: str, budget: float):
        self.client = client
        self.title = title
        self.craft = craft
        self.budget = budget
        self.assigned_guild: Optional[str] = None
        self.status = "quoting"
        self.rating: Optional[float] = None
        self.created = time.time()
        self.id = hashlib.sha256(f"order:{title}".encode()).hexdigest()[:10]

    def accept(self, guild: str, bid: float) -> bool:
        if self.status != "quoting":
            return False
        self.assigned_guild = guild
        self.budget = bid
        self.status = "fulfilling"
        return True

    def complete(self, rating: float = 0.9) -> bool:
        if self.status != "fulfilling":
            return False
        self.rating = max(0.0, min(1.0, rating))
        self.status = "reviewed"
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "client": self.client, "title": self.title,
                "craft": self.craft, "budget": self.budget, "guild": self.assigned_guild,
                "status": self.status, "rating": self.rating}


class GuildOrders:
    """Routes external commissions to the best-fit guild."""

    def __init__(self):
        self._orders: Dict[str, Order] = {}
        self._guild_crafts: Dict[str, str] = {}
        self._fulfilled = 0
        self._revenue = 0.0

    def register_guild(self, guild: str, craft: str) -> None:
        self._guild_crafts[guild] = craft

    def commission(self, client: str, title: str, craft: str, budget: float) -> Order:
        order = Order(client, title, craft, budget)
        self._orders[order.id] = order
        return order

    def route(self, order_id: str, bid: float = 0.0) -> bool:
        order = self._orders.get(order_id)
        if order is None:
            return False
        matches = [g for g, c in self._guild_crafts.items() if c == order.craft]
        if not matches:
            return False
        guild = matches[0]
        final_price = bid if bid > 0 else order.budget
        return order.accept(guild, final_price)

    def complete(self, order_id: str, rating: float = 0.9) -> bool:
        order = self._orders.get(order_id)
        if order is None:
            return False
        ok = order.complete(rating)
        if ok:
            self._fulfilled += 1
            self._revenue += order.budget
        return ok

    def status(self) -> Dict[str, Any]:
        return {"orders": len(self._orders), "guilds": len(self._guild_crafts),
                "fulfilled": self._fulfilled, "revenue": round(self._revenue, 4)}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    orders = GuildOrders()
    return {"status": "active", "module": "guild_orders",
            **orders.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "134", "module": "guild_orders"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
