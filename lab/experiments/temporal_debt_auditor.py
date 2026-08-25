#!/usr/bin/env python3
"""Temporal Debt Auditor — track and audit time-based obligations across the system.

Bridges temporal_debt + chronicle_engine + entropy to create a
comprehensive audit system for agent obligations. Every action creates
debt; debt accrues interest; the auditor tracks who owes what, when
it's due, and what happens when obligations go unfulfilled.

The auditor also detects "debt spirals" — situations where agents
become trapped in escalating obligations — and suggests forgiveness
events to restore systemic health.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Obligation:
    obligation_id: str
    debtor_id: str
    creditor_id: str | None
    description: str
    principal: float
    interest_rate: float
    created_tick: int
    due_tick: int
    fulfilled: bool = False
    fulfilled_tick: int | None = None
    transferred_to: str | None = None

    def current_amount(self, current_tick: int) -> float:
        elapsed = max(0, current_tick - self.created_tick)
        return round(self.principal * math.pow(1 + self.interest_rate, elapsed), 4)

    def is_overdue(self, current_tick: int) -> bool:
        return not self.fulfilled and current_tick > self.due_tick

    def age(self, current_tick: int) -> int:
        return current_tick - self.created_tick


@dataclass
class AuditRecord:
    tick: int
    agent_id: str
    total_debt: float
    debt_count: int
    overdue_count: int
    risk_level: str
    snapshot_hash: str


@dataclass
class TemporalDebtAuditor:
    """Audit system for temporal obligations."""
    critical_ratio: float = 3.0
    warning_ratio: float = 2.0
    default_interest: float = 0.05
    default_window: int = 10
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = __import__("random").Random(self.seed)
        self._obligations: dict[str, Obligation] = {}
        self._ledger: dict[str, list[str]] = defaultdict(list)
        self._audit_trail: list[AuditRecord] = []
        self._forgiveness_events: list[dict[str, Any]] = []
        self._tick = 0

    def incur(self, debtor_id: str, description: str,
              principal: float, creditor_id: str | None = None,
              due_in: int | None = None) -> Obligation:
        due_tick = self._tick + (due_in or self.default_window)
        oid = hashlib.sha256(
            f"{debtor_id}:{description}:{self._tick}".encode()
        ).hexdigest()[:12]

        obligation = Obligation(
            obligation_id=oid,
            debtor_id=debtor_id,
            creditor_id=creditor_id,
            description=description,
            principal=principal,
            interest_rate=self.default_interest,
            created_tick=self._tick,
            due_tick=due_tick,
        )
        self._obligations[oid] = obligation
        self._ledger[debtor_id].append(oid)
        return obligation

    def fulfill(self, obligation_id: str, tick: int | None = None) -> bool:
        tick = tick or self._tick
        obligation = self._obligations.get(obligation_id)
        if not obligation or obligation.fulfilled:
            return False
        obligation.fulfilled = True
        obligation.fulfilled_tick = tick
        return True

    def transfer(self, obligation_id: str, new_debtor: str) -> bool:
        obligation = self._obligations.get(obligation_id)
        if not obligation or obligation.fulfilled:
            return False
        old_debtor = obligation.debtor_id
        obligation.debtor_id = new_debtor
        obligation.transferred_to = new_debtor
        self._ledger[old_debtor] = [
            oid for oid in self._ledger[old_debtor] if oid != obligation_id
        ]
        self._ledger[new_debtor].append(obligation_id)
        return True

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        overdue = [o for o in self._obligations.values() if o.is_overdue(self._tick)]
        return {"tick": self._tick, "overdue_count": len(overdue)}

    def audit_agent(self, agent_id: str) -> AuditRecord:
        agent_obligations = [
            self._obligations[oid]
            for oid in self._ledger.get(agent_id, [])
            if oid in self._obligations and not self._obligations[oid].fulfilled
        ]

        total_debt = sum(o.current_amount(self._tick) for o in agent_obligations)
        total_principal = sum(o.principal for o in agent_obligations)
        overdue = sum(1 for o in agent_obligations if o.is_overdue(self._tick))

        if total_principal > 0:
            ratio = total_debt / total_principal
        else:
            ratio = 0.0

        if ratio >= self.critical_ratio:
            risk = "critical"
        elif ratio >= self.warning_ratio:
            risk = "warning"
        elif overdue > 0:
            risk = "overdue"
        else:
            risk = "healthy"

        snapshot = json.dumps({
            "agent": agent_id,
            "debt": round(total_debt, 4),
            "count": len(agent_obligations),
            "overdue": overdue,
        }, sort_keys=True, separators=(",", ":"))

        record = AuditRecord(
            tick=self._tick,
            agent_id=agent_id,
            total_debt=round(total_debt, 4),
            debt_count=len(agent_obligations),
            overdue_count=overdue,
            risk_level=risk,
            snapshot_hash=hashlib.sha256(snapshot.encode()).hexdigest()[:12],
        )
        self._audit_trail.append(record)
        return record

    def detect_debt_spirals(self) -> list[dict[str, Any]]:
        """Find agents whose debt is growing exponentially."""
        spirals: list[dict[str, Any]] = []
        for agent_id, oids in self._ledger.items():
            obligations = [
                self._obligations[oid] for oid in oids
                if oid in self._obligations and not self._obligations[oid].fulfilled
            ]
            if not obligations:
                continue

            amounts = [o.current_amount(self._tick) for o in obligations]
            total = sum(amounts)
            principal = sum(o.principal for o in obligations)

            if principal > 0 and total / principal >= self.critical_ratio:
                oldest = min(o.created_tick for o in obligations)
                avg_interest = sum(o.interest_rate for o in obligations) / len(obligations)
                spirals.append({
                    "agent_id": agent_id,
                    "total_debt": round(total, 4),
                    "total_principal": round(principal, 4),
                    "ratio": round(total / principal, 4),
                    "oldest_debt_tick": oldest,
                    "avg_interest": round(avg_interest, 4),
                    "obligation_count": len(obligations),
                })

        return sorted(spirals, key=lambda s: -s["ratio"])

    def suggest_forgiveness(self, entropy_budget: float = 10.0) -> list[dict[str, Any]]:
        """Suggest which debts to forgive to restore systemic health."""
        spirals = self.detect_debt_spirals()
        suggestions: list[dict[str, Any]] = []
        remaining_budget = entropy_budget

        for spiral in spirals:
            # Forgive the oldest, highest-interest debt first
            agent_obligations = [
                self._obligations[oid]
                for oid in self._ledger.get(spiral["agent_id"], [])
                if oid in self._obligations and not self._obligations[oid].fulfilled
            ]
            if not agent_obligations:
                continue

            oldest = min(agent_obligations, key=lambda o: o.created_tick)
            forgiveness_cost = oldest.principal * 0.5

            if forgiveness_cost <= remaining_budget:
                suggestions.append({
                    "agent_id": spiral["agent_id"],
                    "forgive_obligation": oldest.obligation_id,
                    "description": oldest.description,
                    "principal": oldest.principal,
                    "cost": round(forgiveness_cost, 4),
                    "health_improvement": round(spiral["ratio"] - self.warning_ratio, 4),
                })
                remaining_budget -= forgiveness_cost

        return suggestions

    def system_health(self) -> dict[str, Any]:
        active = [o for o in self._obligations.values() if not o.fulfilled]
        overdue = [o for o in active if o.is_overdue(self._tick)]
        total_debt = sum(o.current_amount(self._tick) for o in active)
        total_principal = sum(o.principal for o in active)

        return {
            "tick": self._tick,
            "total_obligations": len(self._obligations),
            "active": len(active),
            "fulfilled": len(self._obligations) - len(active),
            "overdue": len(overdue),
            "total_debt": round(total_debt, 4),
            "total_principal": round(total_principal, 4),
            "system_ratio": round(total_debt / total_principal, 4) if total_principal else 0,
            "debt_spirals": len(self.detect_debt_spirals()),
            "audit_records": len(self._audit_trail),
        }


def demo() -> dict[str, Any]:
    auditor = TemporalDebtAuditor(seed=42)

    # Simulate 5 agents incurring debts over 20 ticks
    agents = ["alpha", "beta", "gamma", "delta", "epsilon"]
    for t in range(20):
        auditor.tick()
        for agent in agents:
            if t % 3 == 0:
                auditor.incur(agent, f"action-{t}", principal=1.0 + t * 0.1)
        # Alpha fulfills some debts
        if t % 5 == 0:
            for oid, oblig in list(auditor._obligations.items()):
                if oblig.debtor_id == "alpha" and not oblig.fulfilled:
                    auditor.fulfill(oid)
                    break

    # Audit all agents
    audits = {agent: auditor.audit_agent(agent) for agent in agents}
    spirals = auditor.detect_debt_spirals()
    suggestions = auditor.suggest_forgiveness(entropy_budget=5.0)
    health = auditor.system_health()

    return {
        "audits": {k: {
            "total_debt": v.total_debt,
            "debt_count": v.debt_count,
            "overdue_count": v.overdue_count,
            "risk_level": v.risk_level,
        } for k, v in audits.items()},
        "debt_spirals": spirals,
        "forgiveness_suggestions": suggestions,
        "system_health": health,
    }


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
