"""Temporal debt — actions create future obligations.

Every significant action generates a "debt obligation" — a promise that
must be fulfilled within N ticks. Unfulfilled debts accumulate compound
interest (entropy cost grows exponentially). Agents drowning in debt lose
abilities progressively. Debts can be transferred between agents (creating
emergent economic pressure) or forgiven by authority figures.
"""
from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DebtObligation:
    debt_id: str
    debtor_id: str
    creditor_id: str | None   # Who is owed (None = system)
    description: str
    principal: float           # Original entropy cost
    interest_rate: float       # Per-tick growth rate
    created_tick: int
    due_tick: int

    @property
    def current_amount(self) -> float:
        """Compound interest calculation."""
        elapsed = max(0, self.created_tick - self.created_tick)
        return round(self.principal * math.pow(1 + self.interest_rate, elapsed), 4)

    @property
    def is_overdue(self) -> bool:
        return self.due_tick < self._current_tick if hasattr(self, '_current_tick') else False


class TemporalDebtLedger:
    DEFAULT_INTEREST = 0.05     # 5% per tick
    DEFAULT_DUE_WINDOW = 10     # Ticks before overdue
    CRITICAL_DEBT_RATIO = 3.0   # Debt > 3× principal = critical

    def __init__(self) -> None:
        self._debts: dict[str, list[DebtObligation]] = defaultdict(list)
        self._tick = 0
        self._defaults: set[str] = set()  # Agents who've defaulted

    def incur(self, debtor_id: str, action: str,
              cost: float, creditor_id: str | None = None,
              due_in_ticks: int | None = None) -> DebtObligation:
        """Record a new debt from an action."""
        did = hashlib.sha256(f"{debtor_id}:{action}:{self._tick}".encode()).hexdigest()[:10]
        debt = DebtObligation(
            debt_id=did, debtor_id=debtor_id, creditor_id=creditor_id,
            description=action, principal=max(0.1, cost),
            interest_rate=self.DEFAULT_INTEREST,
            created_tick=self._tick,
            due_tick=self._tick + (due_in_ticks or self.DEFAULT_DUE_WINDOW),
        )
        self._debts[debtor_id].append(debt)
        return debt

    def repay(self, agent_id: str, debt_id: str, amount: float) -> bool:
        """Pay down a specific debt."""
        for debt in self._debts.get(agent_id, []):
            if debt.debt_id == debt_id:
                debt.principal -= amount
                if debt.principal <= 0:
                    self._debts[agent_id].remove(debt)
                return True
        return False

    def forgive(self, authority_id: str, debtor_id: str) -> int:
        """Authority figure forgives all debts. Returns count forgiven."""
        count = len(self._debts.get(debtor_id, []))
        self._debts[debtor_id].clear()
        return count

    def tick(self) -> dict[str, Any]:
        """Process interest accrual and check for defaults."""
        self._tick += 1
        defaulted_this_tick = []
        total_outstanding = {}

        for agent_id, debts in self._debts.items():
            total_owed = sum(d.current_amount * math.pow(1 + d.interest_rate, self._tick - d.created_tick)
                           for d in debts)
            total_outstanding[agent_id] = round(total_owed, 4)

            overdue = [d for d in debts if self._tick - d.created_tick > self.DEFAULT_DUE_WINDOW]
            if overdue and len(overdue) == len(debts):
                if agent_id not in self._defaults:
                    self._defaults.add(agent_id)
                    defaulted_this_tick.append(agent_id)

        return {
            "tick": self._tick,
            "total_debt_holders": len(self._debts),
            "outstanding": dict(sorted(total_outstanding.items(), key=lambda x: -x[1])[:5]),
            "new_defaults": defaulted_this_tick,
            "total_defaults": len(self._defaults),
        }

    @property
    def stats(self) -> dict[str, Any]:
        total_debts = sum(len(v) for v in self._debts.values())
        avg_principal = (
            sum(d.principal for debts in self._debts.values() for d in debts) / max(total_debts, 1)
        )
        return {
            "debt_holders": len(self._debts),
            "total_obligations": total_debts,
            "avg_principal": round(avg_principal, 4),
            "defaulted_agents": len(self._defaults),
        }
