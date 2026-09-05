"""Wave 135 — Tiered Access System.

External clients subscribe to civilization services at tiers: free,
pro, and nexus. Each tier unlocks a set of capabilities and a
capacity quota, giving the workforce a recurring subscription
revenue channel.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional

PLANS = {
    "free": {"price": 0.0, "quota": 10, "features": ["reports"]},
    "pro": {"price": 29.0, "quota": 500, "features": ["reports", "agents", "scenes"]},
    "nexus": {"price": 99.0, "quota": 5000, "features": ["reports", "agents", "scenes", "mutations", "multiverse"]},
}


class Subscriber:
    """An external client with a tiered subscription."""

    def __init__(self, name: str, plan: str):
        self.name = name
        self.plan = plan if plan in PLANS else "free"
        self.usage = 0
        self.created = time.time()
        self.id = hashlib.sha256(f"sub:{name}".encode()).hexdigest()[:10]

    def quota(self) -> int:
        return PLANS[self.plan]["quota"]

    def features(self) -> List[str]:
        return PLANS[self.plan]["features"]

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "plan": self.plan,
                "quota": self.quota(), "usage": self.usage}


class TieredAccessSystem:
    """Manages tiered subscriptions and quota enforcement."""

    def __init__(self):
        self._subscribers: Dict[str, Subscriber] = {}
        self._recurring_value = 0.0

    def subscribe(self, name: str, plan: str) -> Subscriber:
        subscriber = Subscriber(name, plan)
        self._subscribers[subscriber.id] = subscriber
        self._recurring_value += PLANS[subscriber.plan]["price"]
        return subscriber

    def upgrade(self, subscriber_id: str, plan: str) -> bool:
        subscriber = self._subscribers.get(subscriber_id)
        if subscriber is None or plan not in PLANS:
            return False
        delta = PLANS[plan]["price"] - PLANS[subscriber.plan]["price"]
        subscriber.plan = plan
        self._recurring_value += delta
        return True

    def charge_usage(self, subscriber_id: str, amount: int = 1) -> bool:
        subscriber = self._subscribers.get(subscriber_id)
        if subscriber is None:
            return False
        if subscriber.usage + amount > subscriber.quota():
            return False
        subscriber.usage += amount
        return True

    def monthly_recurring(self) -> float:
        return round(self._recurring_value, 4)

    def status(self) -> Dict[str, Any]:
        return {"subscribers": len(self._subscribers),
                "mrr": self.monthly_recurring(),
                "plan_distribution": {
                    p: sum(1 for s in self._subscribers.values() if s.plan == p)
                    for p in PLANS}}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    system = TieredAccessSystem()
    return {"status": "active", "module": "tiered_access_system",
            **system.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "135", "module": "tiered_access_system"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
