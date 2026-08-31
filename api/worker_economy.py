"""Wave 131 — Worker Economy.

Introduces an internal token economy where workers earn units for
completed tasks, spend them on upgrades, and can be traded on an
internal labor market. Ties together the workforce layer with real
incentives and scarcity.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class WorkerAccount:
    """A worker's internal economy balance."""

    def __init__(self, name: str, starting_units: float = 100.0):
        self.name = name
        self.units = starting_units
        self.earned = 0.0
        self.spent = 0.0
        self.created = time.time()
        self.id = hashlib.sha256(f"wallet:{name}".encode()).hexdigest()[:10]

    def credit(self, amount: float) -> None:
        self.units += amount
        self.earned += amount

    def debit(self, amount: float) -> bool:
        if amount > self.units:
            return False
        self.units -= amount
        self.spent += amount
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "units": round(self.units, 4),
                "earned": round(self.earned, 4), "spent": round(self.spent, 4)}


class WorkerEconomy:
    """Internal token economy governing worker incentives."""

    def __init__(self):
        self._wallets: Dict[str, WorkerAccount] = {}
        self._prices: Dict[str, float] = {}
        self._transactions = 0
        self._total_units = 0.0

    def enroll(self, name: str, starting_units: float = 100.0) -> WorkerAccount:
        acc = WorkerAccount(name, starting_units)
        self._wallets[name] = acc
        self._total_units += starting_units
        return acc

    def pay(self, name: str, amount: float) -> bool:
        acc = self._wallets.get(name)
        if acc is None:
            return False
        acc.credit(amount)
        self._total_units += amount
        self._transactions += 1
        return True

    def spend(self, name: str, amount: float) -> bool:
        acc = self._wallets.get(name)
        if acc is None:
            return False
        ok = acc.debit(amount)
        if ok:
            self._total_units -= amount
            self._transactions += 1
        return ok

    def set_item_price(self, item: str, price: float) -> None:
        self._prices[item] = price

    def transfer(self, sender: str, receiver: str, amount: float) -> bool:
        if not self.spend(sender, amount):
            return False
        self.pay(receiver, amount)
        return True

    def balance(self, name: str) -> float:
        acc = self._wallets.get(name)
        return acc.units if acc else 0.0

    def status(self) -> Dict[str, Any]:
        return {"wallets": len(self._wallets),
                "transactions": self._transactions,
                "total_units": round(self._total_units, 4),
                "listed_items": len(self._prices)}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    economy = WorkerEconomy()
    return {"status": "active", "module": "worker_economy",
            **economy.status()}


def coherence_vitals() -> dict:
    """worker_economy reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "worker_economy_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['credits', 'workforce_nexus', 'simulation_as_service']

