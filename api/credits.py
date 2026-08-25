"""Credits & Pay-Per-Use — micro-payments for individual experiment runs.

Instead of subscriptions, users can buy credits and spend them per action.
1 credit = $0.01. Experiment runs cost 1-50 credits depending on complexity.

Usage:
    POST /api/credits/buy        — purchase credits
    GET  /api/credits/balance    — check balance
    POST /api/credits/spend      — spend credits
    GET  /api/credits/history    — transaction history
    GET  /api/credits/pricing    — per-experiment pricing
"""
from __future__ import annotations

import hashlib
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict, List
from dataclasses import dataclass, field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BALANCES_FILE = ROOT / ".runtime" / "credit_balances.json"
TRANSACTIONS_FILE = ROOT / ".runtime" / "credit_transactions.json"

CREDIT_VALUE_USD = 0.01  # 1 credit = $0.01

# Pricing tiers for credits
CREDIT_PACKAGES = {
    "starter": {"credits": 100, "price_usd": 1.00, "bonus": 0},
    "explorer": {"credits": 500, "price_usd": 4.50, "bonus": 50},
    "scientist": {"credits": 2000, "price_usd": 16.00, "bonus": 400},
    "architect": {"credits": 10000, "price_usd": 70.00, "bonus": 3000},
}

EXPERIMENT_COSTS = {
    # Free tier experiments (1 credit)
    "photon_memory": 1, "dark_matter_mapper": 1, "coral_reef_simulator": 1,
    "crystalline_lattice": 1, "neutrino_detector": 1, "fractal_language": 1,
    # Standard experiments (5 credits)
    "quantum_tunneling": 5, "strange_attractor": 5, "phase_transition": 5,
    "sacred_geometry": 5, "myth_generator": 5, "dream_weaver": 5,
    # Advanced experiments (10 credits)
    "reality_synthesis": 10, "cross_pollination_engine": 10,
    "temporal_pattern_recognizer": 10, "information_theory_analyzer": 10,
    "biomimetic_optimizer": 10, "edge_of_chaos": 10,
    # Premium experiments (25 credits)
    "consciousness_simulator": 25, "quantum_superposition_engine": 25,
    "cosmic_web_mapper": 25, "neural_plasticity_simulator": 25,
    "spacetime_manifold": 25, "gravitational_lens": 25,
    # Elite experiments (50 credits)
    "system_orchestrator": 50, "pipeline_engine": 50,
    "cognition_engine": 50, "streaming_reactor": 50,
}


class CreditSystem:
    def __init__(self):
        self.balances: Dict[str, int] = {}
        self.transactions: List[Dict] = []
        self._load()

    def _load(self):
        BALANCES_FILE.parent.mkdir(parents=True, exist_ok=True)
        if BALANCES_FILE.exists():
            self.balances = json.loads(BALANCES_FILE.read_text())
        if TRANSACTIONS_FILE.exists():
            self.transactions = json.loads(TRANSACTIONS_FILE.read_text())

    def _save(self):
        BALANCES_FILE.parent.mkdir(parents=True, exist_ok=True)
        BALANCES_FILE.write_text(json.dumps(self.balances))
        TRANSACTIONS_FILE.write_text(json.dumps(self.transactions[-1000:]))

    def buy_credits(self, user: str, package: str) -> Dict:
        if package not in CREDIT_PACKAGES:
            return {"error": f"unknown package: {package}"}
        pkg = CREDIT_PACKAGES[package]
        total_credits = pkg["credits"] + pkg["bonus"]
        self.balances[user] = self.balances.get(user, 0) + total_credits
        self.transactions.append({
            "user": user, "type": "purchase", "amount": total_credits,
            "price_usd": pkg["price_usd"], "package": package,
            "time": time.time(),
        })
        self._save()
        return {
            "purchased": True, "package": package,
            "credits_added": total_credits, "bonus": pkg["bonus"],
            "balance": self.balances[user],
        }

    def get_balance(self, user: str) -> int:
        return self.balances.get(user, 0)

    def spend(self, user: str, amount: int, description: str = "") -> Dict:
        balance = self.balances.get(user, 0)
        if balance < amount:
            return {"success": False, "error": "insufficient credits",
                    "balance": balance, "required": amount}
        self.balances[user] = balance - amount
        self.transactions.append({
            "user": user, "type": "spend", "amount": -amount,
            "description": description, "time": time.time(),
        })
        self._save()
        return {"success": True, "spent": amount, "balance": self.balances[user]}

    def spend_for_experiment(self, user: str, experiment_name: str) -> Dict:
        cost = EXPERIMENT_COSTS.get(experiment_name, 10)
        return self.spend(user, cost, f"run:{experiment_name}")

    def get_history(self, user: str, limit: int = 20) -> List[Dict]:
        user_txns = [t for t in self.transactions if t["user"] == user]
        return user_txns[-limit:]

    def get_pricing(self) -> Dict:
        return {
            "packages": CREDIT_PACKAGES,
            "experiment_costs": EXPERIMENT_COSTS,
            "credit_value_usd": CREDIT_VALUE_USD,
        }


def handler(request, response):
    return CreditSystem().get_pricing()


def demo():
    system = CreditSystem()
    print("=== Credits & Pay-Per-Use System ===")
    print(f"\nCredit packages:")
    for name, pkg in CREDIT_PACKAGES.items():
        print(f"  {name}: {pkg['credits']}+{pkg['bonus']} credits = ${pkg['price_usd']}")

    result = system.buy_credits("user_1", "explorer")
    print(f"\nBought explorer: {result['credits_added']} credits (balance={result['balance']})")

    run = system.spend_for_experiment("user_1", "quantum_tunneling")
    print(f"Run quantum_tunneling: {run}")

    run2 = system.spend_for_experiment("user_1", "reality_synthesis")
    print(f"Run reality_synthesis: {run2}")

    balance = system.get_balance("user_1")
    print(f"\nFinal balance: {balance} credits (${balance * CREDIT_VALUE_USD:.2f})")

    history = system.get_history("user_1")
    print(f"Transaction history: {len(history)} entries")

    return system.get_pricing()


if __name__ == "__main__":
    demo()
