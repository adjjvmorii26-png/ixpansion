"""Temporal Arbitrage — buy low in one time period, sell high in another.

Exploits price differences across time. Users set up "time bridges"
that automatically buy resources when cheap and sell when expensive.
The system monitors price curves and executes arbitrage when profitable.

Usage:
    POST /api/arb/setup             — set up an arbitrage bridge
    POST /api/arb/execute           — manually execute an arbitrage
    GET  /api/arb/bridges           — list active arbitrage bridges
    GET  /api/arb/opportunities     — current opportunities
    GET  /api/arb/history           — arbitrage history
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RESOURCES = {
    "compute_hour": {"volatility": 0.15, "base_price": 1.0},
    "storage_gb": {"volatility": 0.08, "base_price": 0.10},
    "agent_cycle": {"volatility": 0.20, "base_price": 0.50},
    "quantum_shot": {"volatility": 0.30, "base_price": 0.01},
    "dream_output": {"volatility": 0.25, "base_price": 2.0},
    "entropy_unit": {"volatility": 0.35, "base_price": 0.25},
}


class TemporalArbitrage:
    def __init__(self):
        self.bridges: Dict[str, Dict] = {}
        self.history: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "temporal_arb.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.bridges = data.get("bridges", {})
            self.history = data.get("history", [])

    def _save(self):
        path = ROOT / ".runtime" / "temporal_arb.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "bridges": self.bridges,
            "history": self.history[-500:],
        }, indent=2))

    def setup(self, resource: str, user: str, buy_threshold: float,
              sell_threshold: float, quantity: int = 10) -> Dict:
        if resource not in RESOURCES:
            return {"error": f"unknown resource: {resource}"}
        if sell_threshold <= buy_threshold:
            return {"error": "sell threshold must be > buy threshold"}
        bridge_id = hashlib.sha256(f"{user}:{resource}:{time.time()}".encode()).hexdigest()[:10]
        self.bridges[bridge_id] = {
            "resource": resource, "user": user,
            "buy_threshold": buy_threshold,
            "sell_threshold": sell_threshold,
            "quantity": quantity,
            "trades": 0, "total_profit": 0.0,
            "status": "active", "created": time.time(),
        }
        self._save()
        return {
            "bridge_id": bridge_id, "resource": resource,
            "buy_below": buy_threshold, "sell_above": sell_threshold,
        }

    def execute(self, bridge_id: str, current_price: float) -> Dict:
        if bridge_id not in self.bridges:
            return {"error": "bridge not found"}
        bridge = self.bridges[bridge_id]
        if bridge["status"] != "active":
            return {"error": "bridge not active"}
        resource = bridge["resource"]
        vol = RESOURCES[resource]["volatility"]
        if current_price <= bridge["buy_threshold"]:
            action = "buy"
            profit = round((bridge["sell_threshold"] - current_price) * bridge["quantity"], 4)
        elif current_price >= bridge["sell_threshold"]:
            action = "sell"
            profit = round((current_price - bridge["buy_threshold"]) * bridge["quantity"], 4)
        else:
            return {
                "action": "hold",
                "current_price": current_price,
                "buy_below": bridge["buy_threshold"],
                "sell_above": bridge["sell_threshold"],
                "spread": round(bridge["sell_threshold"] - current_price, 4),
            }
        actual_profit = round(profit * (0.8 + random.uniform(0, 0.2)), 4)  # Market friction
        bridge["trades"] += 1
        bridge["total_profit"] = round(bridge["total_profit"] + actual_profit, 4)
        record = {
            "bridge_id": bridge_id, "action": action,
            "resource": resource, "price": current_price,
            "quantity": bridge["quantity"],
            "profit": actual_profit,
            "total_profit": bridge["total_profit"],
            "trade_number": bridge["trades"],
            "timestamp": time.time(),
        }
        self.history.append(record)
        self._save()
        return record

    def bridges_list(self) -> List[Dict]:
        return [{"id": k, **v} for k, v in self.bridges.items()]

    def opportunities(self) -> List[Dict]:
        opps = []
        for res, spec in RESOURCES.items():
            current = spec["base_price"] * (1 + random.uniform(-spec["volatility"], spec["volatility"]))
            for bid, bridge in self.bridges.items():
                if bridge["resource"] == res and bridge["status"] == "active":
                    if current <= bridge["buy_threshold"]:
                        opps.append({"resource": res, "action": "buy", "price": round(current, 4),
                                     "threshold": bridge["buy_threshold"], "bridge": bid})
                    elif current >= bridge["sell_threshold"]:
                        opps.append({"resource": res, "action": "sell", "price": round(current, 4),
                                     "threshold": bridge["sell_threshold"], "bridge": bid})
        return opps

    def history_log(self, limit: int = 20) -> List[Dict]:
        return self.history[-limit:]


def handler(request, response):
    ta = TemporalArbitrage()
    return {"resources": list(RESOURCES.keys()), "bridges": len(ta.bridges)}


def demo():
    ta = TemporalArbitrage()
    print("=== Temporal Arbitrage ===")
    bridge = ta.setup("quantum_shot", "trader_1", buy_threshold=0.008, sell_threshold=0.015)
    print(f"\nBridge: {bridge['bridge_id']}")
    print(f"  Buy below: {bridge['buy_below']}, Sell above: {bridge['sell_above']}")

    result = ta.execute(bridge["bridge_id"], current_price=0.005)
    print(f"\nTrade: {result['action']} at ${result['price']}, profit=${result['profit']}")

    result2 = ta.execute(bridge["bridge_id"], current_price=0.018)
    print(f"Trade: {result2['action']} at ${result2['price']}, profit=${result2['profit']}")

    opps = ta.opportunities()
    print(f"\nOpportunities: {len(opps)}")
    stats = {"bridges": len(ta.bridges), "trades": len(ta.history)}
    return stats


if __name__ == "__main__":
    demo()
