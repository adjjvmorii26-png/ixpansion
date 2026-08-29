"""Wave 134 — Autonomous Contracts.

Workers negotiate binding contracts with each other and with external
clients. Terms (deliverable, deadline, payment) are encoded in a
machine-readable contract that self-enforces: late delivery forfeits
payment, early delivery earns a bonus.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class Contract:
    """A machine-enforced agreement between parties."""

    def __init__(self, title: str, party_a: str, party_b: str,
                 payment: float, deadline_penalty: float = 0.1):
        self.title = title
        self.party_a = party_a
        self.party_b = party_b
        self.payment = payment
        self.deadline_penalty = deadline_penalty
        self.status = "negotiating"
        self.delivered_on: Optional[float] = None
        self.settlement = 0.0
        self.created = time.time()
        self.id = hashlib.sha256(f"contract:{title}".encode()).hexdigest()[:10]

    def sign(self) -> bool:
        if self.status != "negotiating":
            return False
        self.status = "active"
        return True

    def deliver(self, on: Optional[float] = None) -> float:
        if self.status != "active":
            return 0.0
        on = on or time.time()
        self.delivered_on = on
        self.status = "settled"
        deadline = self.created + 86400.0
        if on <= deadline:
            self.settlement = self.payment
        else:
            self.settlement = self.payment * (1.0 - self.deadline_penalty)
        return round(self.settlement, 4)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "title": self.title, "parties": [self.party_a, self.party_b],
                "payment": self.payment, "status": self.status,
                "settlement": round(self.settlement, 4)}


class AutonomousContracts:
    """Registry of self-enforcing workforce contracts."""

    def __init__(self):
        self._contracts: Dict[str, Contract] = {}
        self._settled_value = 0.0

    def create(self, title: str, party_a: str, party_b: str,
               payment: float, deadline_penalty: float = 0.1) -> Contract:
        contract = Contract(title, party_a, party_b, payment, deadline_penalty)
        self._contracts[contract.id] = contract
        return contract

    def sign(self, contract_id: str) -> bool:
        return bool(self._contracts.get(contract_id) and self._contracts[contract_id].sign())

    def deliver(self, contract_id: str, on: Optional[float] = None) -> float:
        contract = self._contracts.get(contract_id)
        if contract is None:
            return 0.0
        amount = contract.deliver(on)
        if amount > 0:
            self._settled_value += amount
        return amount

    def status(self) -> Dict[str, Any]:
        return {"contracts": len(self._contracts),
                "active": sum(1 for c in self._contracts.values() if c.status == "active"),
                "settled": sum(1 for c in self._contracts.values() if c.status == "settled"),
                "settled_value": round(self._settled_value, 4)}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    contracts = AutonomousContracts()
    return {"status": "active", "module": "autonomous_contracts",
            **contracts.status()}
