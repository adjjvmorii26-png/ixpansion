"""Entropy Currency — agents earn, spend, and trade chaos as currency.

Entropy is the fundamental currency of IXpansion. Agents earn entropy
by performing work, create it through random actions, and spend it to
influence the system. The entropy market fluctuates based on supply and demand.
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


class EntropyWallet:
    def __init__(self, agent_id: str, balance: float = 100.0):
        self.agent_id = agent_id
        self.balance = balance
        self.transactions: List[Dict[str, Any]] = []
        self.earned_total = 0.0
        self.spent_total = 0.0

    def earn(self, amount: float, source: str = "work") -> Dict[str, Any]:
        amount = max(amount, 0)
        self.balance += amount
        self.earned_total += amount
        tx = {
            "type": "earn",
            "amount": round(amount, 4),
            "source": source,
            "balance_after": round(self.balance, 4),
            "timestamp": time.time(),
        }
        self.transactions.append(tx)
        return tx

    def spend(self, amount: float, purpose: str = "influence") -> Dict[str, Any]:
        if amount > self.balance:
            return {"error": "insufficient entropy", "balance": round(self.balance, 4)}
        self.balance -= amount
        self.spent_total += amount
        tx = {
            "type": "spend",
            "amount": round(amount, 4),
            "purpose": purpose,
            "balance_after": round(self.balance, 4),
            "timestamp": time.time(),
        }
        self.transactions.append(tx)
        return tx

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "balance": round(self.balance, 4),
            "earned_total": round(self.earned_total, 4),
            "spent_total": round(self.spent_total, 4),
            "transaction_count": len(self.transactions),
        }


class EntropyMarket:
    def __init__(self):
        self.wallets: Dict[str, EntropyWallet] = {}
        self.price_history: List[Dict[str, Any]] = []
        self.current_price = 1.0
        self.supply = 0.0
        self.demand = 0.0
        self._tick = 0

    def register(self, agent_id: str, balance: float = 100.0) -> Dict[str, Any]:
        wallet = EntropyWallet(agent_id, balance)
        self.wallets[agent_id] = wallet
        self.supply += balance
        return wallet.to_dict()

    def earn(self, agent_id: str, amount: float, source: str = "work") -> Dict[str, Any]:
        if agent_id not in self.wallets:
            self.register(agent_id)
        result = self.wallets[agent_id].earn(amount, source)
        if "error" not in result:
            self.supply += amount
        return result

    def spend(self, agent_id: str, amount: float, purpose: str = "influence") -> Dict[str, Any]:
        if agent_id not in self.wallets:
            return {"error": "wallet not found"}
        result = self.wallets[agent_id].spend(amount, purpose)
        if "error" not in result:
            self.demand += amount
        return result

    def transfer(self, from_id: str, to_id: str, amount: float) -> Dict[str, Any]:
        if from_id not in self.wallets or to_id not in self.wallets:
            return {"error": "wallet not found"}
        spend_result = self.wallets[from_id].spend(amount, f"transfer to {to_id}")
        if "error" in spend_result:
            return spend_result
        self.wallets[to_id].earn(amount, f"transfer from {from_id}")
        return {"status": "transferred", "from": from_id, "to": to_id, "amount": amount}

    def tick(self) -> Dict[str, Any]:
        """Advance the market by one tick — price adjusts based on supply/demand."""
        self._tick += 1
        ratio = self.demand / max(self.supply, 1.0)
        self.current_price = 0.5 + ratio * 2.0
        self.current_price *= random.uniform(0.95, 1.05)
        self.current_price = max(0.1, min(self.current_price, 10.0))
        entry = {
            "tick": self._tick,
            "price": round(self.current_price, 4),
            "supply": round(self.supply, 4),
            "demand": round(self.demand, 4),
            "timestamp": time.time(),
        }
        self.price_history.append(entry)
        return entry

    def leaderboard(self) -> List[Dict[str, Any]]:
        return sorted(
            [w.to_dict() for w in self.wallets.values()],
            key=lambda x: x["balance"],
            reverse=True,
        )

    def market_stats(self) -> Dict[str, Any]:
        return {
            "total_wallets": len(self.wallets),
            "total_supply": round(self.supply, 4),
            "total_demand": round(self.demand, 4),
            "current_price": round(self.current_price, 4),
            "ticks": self._tick,
            "top_holder": self.leaderboard()[0] if self.wallets else None,
        }


_market = EntropyMarket()


def entropy_currency_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "register":
        return _market.register(
            payload.get("agent_id", f"agent_{random.randint(1000,9999)}"),
            payload.get("balance", 100.0),
        )
    elif action == "earn":
        return _market.earn(
            payload.get("agent_id", "agent"),
            payload.get("amount", 10.0),
            payload.get("source", "work"),
        )
    elif action == "spend":
        return _market.spend(
            payload.get("agent_id", "agent"),
            payload.get("amount", 10.0),
            payload.get("purpose", "influence"),
        )
    elif action == "transfer":
        return _market.transfer(
            payload.get("from", ""), payload.get("to", ""),
            payload.get("amount", 10.0),
        )
    elif action == "tick":
        return _market.tick()
    elif action == "leaderboard":
        return {"leaderboard": _market.leaderboard()}
    return {"status": "active", **_market.market_stats()}
