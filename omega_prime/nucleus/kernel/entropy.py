"""Entropy budget system.

Each agent carries an entropy reservoir. Chaotic actions drain it;
ordered actions replenish it. When depleted, the agent enters
"thermal lockdown" and can only perform zero-entropy actions until
the budget recovers.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EntropyLedger:
    """Tracks an individual agent's thermodynamic account."""

    capacity: float = 100.0
    level: float = -1  # sentinel; set to capacity in __post_init__
    regeneration_rate: float = 0.5
    _lockout: bool = False

    def __post_init__(self):
        if self.level < 0:
            self.level = self.capacity

    @property
    def is_locked(self) -> bool:
        return self._lockout

    @property
    def pressure(self) -> float:
        """How close to lockout, 0.0 = calm, 1.0 = critical."""
        return max(0.0, 1.0 - (self.level / self.capacity)) if self.capacity > 0 else 1.0

    def spend(self, cost: float) -> bool:
        """Attempt to spend entropy. Returns False if locked or insufficient."""
        if self._lockout:
            return False
        if self.level < cost:
            self._lockout = True
            return False
        self.level -= cost
        if self.level <= 0.0:
            self._lockout = True
        return True

    def regenerate(self, multiplier: float = 1.0) -> None:
        """Recover entropy. Called once per pulse."""
        if not self._lockout:
            self.level = min(self.capacity, self.level + self.regeneration_rate * multiplier)
        else:
            # In lockout, recovery is slower but guaranteed
            self.level = min(self.capacity * 0.3, self.level + self.regeneration_rate * 0.25)
            if self.level >= self.capacity * 0.15:
                self._lockout = False


def classify_entropy(action: dict[str, Any]) -> float:
    """Assign an entropy cost to an action based on its nature."""
    intent = action.get("intent", "")
    base_costs: dict[str, float] = {
        "idle": 0.0,
        "observe": 0.1,
        "move": 1.0,
        "patrol": 0.8,
        "construct": 5.0,
        "alert": 3.0,
        "attack": 12.0,
        "teleport": 25.0,
        "create_realm": 50.0,
    }
    # Unknown intents get moderate cost proportional to string length (chaos proxy)
    return base_costs.get(intent, math.sqrt(len(intent)))


class EntropyGovernor:
    """System-wide entropy manager that mediates all agent actions."""

    def __init__(self) -> None:
        self._ledgers: dict[str, EntropyLedger] = {}

    def enroll(self, agent_id: str, capacity: float = 100.0) -> None:
        self._ledgers[agent_id] = EntropyLedger(capacity=capacity)

    def authorize(self, agent_id: str, action: dict[str, Any]) -> tuple[bool, float]:
        """Check if an agent can afford an action. Returns (allowed, cost)."""
        ledger = self._ledgers.get(agent_id)
        if not ledger:
            return True, 0.0
        cost = classify_entropy(action)
        allowed = ledger.spend(cost)
        return allowed, cost

    def tick(self) -> dict[str, dict[str, Any]]:
        """Regenerate all ledgers. Returns status report."""
        report = {}
        for aid, ledger in self._ledgers.items():
            ledger.regenerate()
            report[aid] = {
                "level": round(ledger.level, 1),
                "pressure": round(ledger.pressure, 2),
                "locked": ledger.is_locked,
            }
        return report
