from dataclasses import dataclass, field
from typing import Any


@dataclass
class Resource:
    name: str
    amount: float
    unit_price: float = 1.0


class Economy:
    """Simple resource exchange with supply/demand price adjustment."""

    def __init__(self) -> None:
        self._resources: dict[str, Resource] = {}

    def add_resource(self, name: str, amount: float, base_price: float = 1.0) -> None:
        self._resources[name] = Resource(name=name, amount=amount, unit_price=base_price)

    def trade(self, buyer_id: str, resource_name: str, quantity: float) -> dict[str, Any]:
        res = self._resources.get(resource_name)
        if not res or res.amount < quantity:
            return {"status": "failed", "reason": "insufficient_supply"}
        cost = quantity * res.unit_price
        res.amount -= quantity
        # Simple demand pressure: fewer resources -> higher price
        if res.amount < 10.0:
            res.unit_price *= 1.05
        elif res.amount > 1000.0:
            res.unit_price *= 0.95
        return {"status": "ok", "buyer": buyer_id, "resource": resource_name,
                "quantity": quantity, "cost": round(cost, 2)}

    @property
    def prices(self) -> dict[str, float]:
        return {r.name: r.unit_price for r in self._resources.values()}
