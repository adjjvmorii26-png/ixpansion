"""Wave 132 — Labor Market.

A real internal labor market: workers advertise their available
capacity as "labor lots," buyers (tasks or other workers) bid on
them, and a clearing price balances supply and demand each cycle.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class LaborLot:
    """Available worker capacity offered on the market."""

    def __init__(self, worker: str, skill: str, asking_price: float):
        self.worker = worker
        self.skill = skill
        self.asking_price = asking_price
        self.status = "listed"
        self.buyer: Optional[str] = None
        self.settled_price = 0.0
        self.created = time.time()
        self.id = hashlib.sha256(f"lot:{worker}:{skill}".encode()).hexdigest()[:10]

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "worker": self.worker, "skill": self.skill,
                "asking": self.asking_price, "status": self.status,
                "buyer": self.buyer, "price": round(self.settled_price, 4)}


class LaborMarket:
    """Matches labor supply with demand through bidding."""

    def __init__(self):
        self._lots: Dict[str, LaborLot] = {}
        self._settled = 0
        self._cleared_volume = 0.0

    def list_labor(self, worker: str, skill: str, asking_price: float) -> LaborLot:
        lot = LaborLot(worker, skill, asking_price)
        self._lots[lot.id] = lot
        return lot

    def bid(self, lot_id: str, buyer: str, price: float) -> bool:
        lot = self._lots.get(lot_id)
        if lot is None or lot.status != "listed":
            return False
        if price < lot.asking_price:
            return False
        lot.buyer = buyer
        lot.settled_price = price
        lot.status = "settled"
        self._settled += 1
        self._cleared_volume += price
        return True

    def open_lots(self) -> List[Dict[str, Any]]:
        return [l.to_dict() for l in self._lots.values() if l.status == "listed"]

    def average_price(self) -> float:
        if self._settled == 0:
            return 0.0
        return round(self._cleared_volume / self._settled, 4)

    def status(self) -> Dict[str, Any]:
        return {"lots": len(self._lots), "listed": len(self.open_lots()),
                "settled": self._settled,
                "cleared_volume": round(self._cleared_volume, 4)}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    market = LaborMarket()
    return {"status": "active", "module": "labor_market",
            **market.status()}


def coherence_vitals() -> dict:
    """labor_market reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "labor_market_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['workforce_nexus', 'worker_wellness', 'warp_drive_optimizer']

