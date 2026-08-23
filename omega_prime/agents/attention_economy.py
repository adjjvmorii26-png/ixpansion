"""Attention economy — visibility as currency.

Each agent has a finite attention budget per tick. Observing another
agent costs attention; being observed generates it. High-attention
agents gain influence (their actions carry more weight in consensus).
Low-attention agents become invisible and cannot affect consensus.

This creates a meta-game: agents must balance spending attention on
gathering intelligence vs. performing visible acts to earn it back.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

COST_PER_OBSERVATION = 1.0
REWARD_PER_BEING_OBSERVED = 0.5
MAX_ATTENTION = 50.0


@dataclass
class AttentionLedger:
    agent_id: str
    balance: float = 10.0       # Starting capital
    earned_this_tick: float = 0.0
    spent_this_tick: float = 0.0

    @property
    def is_solvent(self) -> bool:
        return self.balance > 0.0

    @property
    def influence_weight(self) -> float:
        """Influence scales with wealth (attention)."""
        return min(3.0, max(0.1, self.balance / 10.0))


class AttentionEconomy:
    def __init__(self) -> None:
        self._ledgers: dict[str, AttentionLedger] = {}
        self._observation_log: list[dict[str, Any]] = []
        self._tick = 0

    def enroll(self, agent_id: str, starting_balance: float = 10.0) -> None:
        self._ledgers[agent_id] = AttentionLedger(agent_id=agent_id, balance=starting_balance)

    def observe(self, observer_id: str, target_id: str) -> dict[str, Any]:
        """Observer pays attention to target. Observer loses, target gains."""
        self._tick += 1
        observer = self._ledgers.get(observer_id)
        target = self._ledgers.get(target_id)

        if not observer or not target:
            return {"status": "unknown_agent"}

        if not observer.is_solvent:
            return {"status": "observer_bankrupt", "balance": round(observer.balance, 2)}

        cost = COST_PER_OBSERVATION
        reward = REWARD_PER_BEING_OBSERVED * target.influence_weight

        observer.balance -= cost
        observer.spent_this_tick += cost
        target.balance = min(MAX_ATTENTION, target.balance + reward)
        target.earned_this_tick += reward

        record = {
            "tick": self._tick, "observer": observer_id,
            "target": target_id, "cost": cost, "reward": round(reward, 4),
        }
        self._observation_log.append(record)
        return {
            "status": "ok",
            "observer_balance": round(observer.balance, 2),
            "target_balance": round(target.balance, 2),
            "target_influence": round(target.influence_weight, 3),
        }

    def perform_visible_action(self, agent_id: str, action_type: str) -> float:
        """Actions generate attention from the environment (ambient observation)."""
        ledger = self._ledgers.get(agent_id)
        if not ledger:
            return 0.0

        action_visibility = {
            "idle": 0.0, "observe": 0.2, "move": 0.5,
            "attack": 2.0, "construct": 1.5, "alert": 1.8,
            "create_realm": 5.0, "teleport": 4.0,
        }
        reward = action_visibility.get(action_type, 0.1)
        ledger.balance = min(MAX_ATTENTION, ledger.balance + reward)
        ledger.earned_this_tick += reward
        return reward

    def reset_tick(self) -> None:
        """Clear per-tick counters at start of new tick."""
        for ledger in self._ledgers.values():
            ledger.earned_this_tick = 0.0
            ledger.spent_this_tick = 0.0

    def transfer(self, from_id: str, to_id: str, amount: float) -> bool:
        """Agents can gift attention to allies."""
        giver = self._ledgers.get(from_id)
        receiver = self._ledgers.get(to_id)
        if not giver or not receiver or giver.balance < amount:
            return False
        giver.balance -= amount
        receiver.balance = min(MAX_ATTENTION, receiver.balance + amount)
        return True

    @property
    def rich_list(self) -> list[dict[str, Any]]:
        sorted_ledgers = sorted(self._ledgers.values(), key=lambda l: -l.balance)
        return [
            {"agent": l.agent_id, "balance": round(l.balance, 2),
             "influence": round(l.influence_weight, 3), "solvent": l.is_solvent}
            for l in sorted_ledgers[:10]
        ]

    @property
    def stats(self) -> dict[str, Any]:
        total = sum(l.balance for l in self._ledgers.values())
        bankrupt = sum(1 for l in self._ledgers.values() if not l.is_solvent)
        gini = self._gini()
        return {
            "agents": len(self._ledgers),
            "total_attention_circulating": round(total, 2),
            "bankrupt_agents": bankrupt,
            "gini_coefficient": gini,
        }

    def _gini(self) -> float:
        """Measure inequality of attention distribution (0=equal, 1=all concentrated)."""
        balances = sorted(l.balance for l in self._ledgers.values())
        n = len(balances)
        if n == 0 or sum(balances) == 0:
            return 0.0
        cumsum = 0.0
        weighted_sum = 0.0
        for i, b in enumerate(balances):
            weighted_sum += (i + 1) * b
            cumsum += b
        return round((2 * weighted_sum) / (n * cumsum) - (n + 1) / n, 4)
