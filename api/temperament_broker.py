"""Temperament Broker — agents trade personality traits on an open market.

Agents can sell their excess traits (too much aggression, not enough patience)
and buy what they lack. The broker matches sellers and buyers, computes
fair prices, and tracks the resulting personality shifts across the ecosystem.
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

TRAIT_VALUES = {
    "aggression": 0.8, "patience": 0.6, "empathy": 0.7,
    "caution": 0.5, "boldness": 0.9, "humor": 0.4,
    "focus": 0.8, "adaptability": 0.7, "loyalty": 0.6,
    "curiosity": 0.9, "discipline": 0.5, "creativity": 0.8,
}


class TemperamentProfile:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.traits: Dict[str, float] = {
            t: random.uniform(0.1, 1.0) for t in TRAIT_VALUES
        }
        self.credits = 100.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "traits": {k: round(v, 3) for k, v in self.traits.items()},
            "credits": round(self.credits, 2),
        }


class TemperamentBroker:
    def __init__(self):
        self.profiles: Dict[str, TemperamentProfile] = {}
        self.trade_log: List[Dict[str, Any]] = []
        self.market_prices: Dict[str, float] = dict(TRAIT_VALUES)

    def register(self, agent_id: str) -> Dict[str, Any]:
        profile = TemperamentProfile(agent_id)
        self.profiles[agent_id] = profile
        return {"registered": profile.to_dict()}

    def list_sell_orders(self, agent_id: str) -> List[Dict[str, Any]]:
        if agent_id not in self.profiles:
            return []
        profile = self.profiles[agent_id]
        return [
            {"trait": t, "amount": round(v, 3), "price": round(self.market_prices.get(t, 0.5), 2)}
            for t, v in profile.traits.items() if v > 0.5
        ]

    def list_buy_orders(self, agent_id: str) -> List[Dict[str, Any]]:
        if agent_id not in self.profiles:
            return []
        profile = self.profiles[agent_id]
        return [
            {"trait": t, "need": round(1.0 - v, 3), "price": round(self.market_prices.get(t, 0.5), 2)}
            for t, v in profile.traits.items() if v < 0.5
        ]

    def execute_trade(self, seller_id: str, buyer_id: str, trait: str, amount: float) -> Dict[str, Any]:
        if seller_id not in self.profiles or buyer_id not in self.profiles:
            return {"error": "agent not found"}
        seller = self.profiles[seller_id]
        buyer = self.profiles[buyer_id]
        if seller.traits.get(trait, 0) < amount:
            return {"error": "insufficient trait"}
        price = self.market_prices.get(trait, 0.5) * amount
        if buyer.credits < price:
            return {"error": "insufficient credits"}
        seller.traits[trait] -= amount
        buyer.traits[trait] = buyer.traits.get(trait, 0) + amount
        seller.credits += price
        buyer.credits -= price
        self.market_prices[trait] *= random.uniform(0.95, 1.05)
        trade = {
            "seller": seller_id, "buyer": buyer_id,
            "trait": trait, "amount": round(amount, 3),
            "price": round(price, 2), "time": time.time(),
        }
        self.trade_log.append(trade)
        return {"trade": trade}

    def market_overview(self) -> Dict[str, Any]:
        return {trait: round(price, 3) for trait, price in self.market_prices.items()}

    def broker_stats(self) -> Dict[str, Any]:
        return {
            "total_agents": len(self.profiles),
            "total_trades": len(self.trade_log),
            "market_traits": len(self.market_prices),
        }


_broker = TemperamentBroker()


def temperament_broker_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "register":
        return _broker.register(payload.get("agent_id", f"agent_{random.randint(1000,9999)}"))
    elif action == "sell_orders":
        return {"orders": _broker.list_sell_orders(payload.get("agent_id", ""))}
    elif action == "buy_orders":
        return {"orders": _broker.list_buy_orders(payload.get("agent_id", ""))}
    elif action == "trade":
        return _broker.execute_trade(
            payload.get("seller", ""), payload.get("buyer", ""),
            payload.get("trait", "patience"), payload.get("amount", 0.1),
        )
    elif action == "market":
        return {"market": _broker.market_overview()}
    return {"status": "active", **_broker.broker_stats()}
