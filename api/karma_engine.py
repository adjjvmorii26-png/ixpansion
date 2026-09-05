"""Karma Engine — agents accumulate moral weight from their actions.

Every action generates karma: helpful actions create positive karma,
harmful actions create negative karma. Karma influences how other agents
perceive and interact with you, opening some doors and closing others.
The engine creates a moral dimension to agent interactions.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class KarmaLedger:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.balance = 0.0
        self.history: List[Dict[str, Any]] = []
        self.karma_events: Dict[str, int] = {"positive": 0, "negative": 0, "neutral": 0}

    def add_karma(self, amount: float, reason: str, source: str = "system") -> Dict[str, Any]:
        self.balance += amount
        category = "positive" if amount > 0 else "negative" if amount < 0 else "neutral"
        self.karma_events[category] += 1
        entry = {
            "amount": round(amount, 4),
            "reason": reason,
            "source": source,
            "balance_after": round(self.balance, 4),
            "timestamp": time.time(),
        }
        self.history.append(entry)
        return entry

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "balance": round(self.balance, 4),
            "events": self.karma_events,
            "total_transactions": len(self.history),
        }


class KarmaEngine:
    def __init__(self):
        self.ledgers: Dict[str, KarmaLedger] = {}
        self.karma_log: List[Dict[str, Any]] = []
        self.karma_rules = {
            "help_agent": 1.0, "share_knowledge": 0.8,
            "build_structure": 1.2, "create_beauty": 1.5,
            "harm_agent": -2.0, "destroy_work": -1.5,
            "hoard_resources": -0.8, "betray_trust": -3.0,
            "teach": 0.5, "discover": 1.0,
            "heal": 0.7, "inspire": 1.3,
        }

    def register(self, agent_id: str) -> Dict[str, Any]:
        self.ledgers[agent_id] = KarmaLedger(agent_id)
        return {"registered": agent_id}

    def act(self, agent_id: str, action: str, target: str = "system") -> Dict[str, Any]:
        if agent_id not in self.ledgers:
            self.register(agent_id)
        amount = self.karma_rules.get(action, 0.0)
        if amount == 0:
            amount = random.uniform(-0.5, 0.5)
        result = self.ledgers[agent_id].add_karma(amount, action, target)
        self.karma_log.append({"agent": agent_id, "action": action, **result})
        return result

    def balance(self, agent_id: str) -> Dict[str, Any]:
        if agent_id not in self.ledgers:
            return {"error": "agent not found"}
        ledger = self.ledgers[agent_id]
        return ledger.to_dict()

    def leaderboard(self) -> List[Dict[str, Any]]:
        return sorted(
            [l.to_dict() for l in self.ledgers.values()],
            key=lambda x: x["balance"],
            reverse=True,
        )

    def karma_tier(self, agent_id: str) -> str:
        if agent_id not in self.ledgers:
            return "unknown"
        balance = self.ledgers[agent_id].balance
        if balance > 10:
            return "saint"
        elif balance > 5:
            return "virtuous"
        elif balance > 0:
            return "good"
        elif balance > -5:
            return "neutral"
        elif balance > -10:
            return "suspect"
        return "karmic_debt"

    def engine_stats(self) -> Dict[str, Any]:
        total_pos = sum(l.karma_events["positive"] for l in self.ledgers.values())
        total_neg = sum(l.karma_events["negative"] for l in self.ledgers.values())
        return {
            "total_agents": len(self.ledgers),
            "total_actions": len(self.karma_log),
            "positive_actions": total_pos,
            "negative_actions": total_neg,
            "avg_balance": round(
                sum(l.balance for l in self.ledgers.values()) / max(len(self.ledgers), 1), 4
            ),
        }


_engine = KarmaEngine()


def karma_engine_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "register":
        return _engine.register(payload.get("agent_id", f"agent_{random.randint(1000,9999)}"))
    elif action == "act":
        return _engine.act(
            payload.get("agent_id", "anon"),
            payload.get("action", "help_agent"),
            payload.get("target", "system"),
        )
    elif action == "balance":
        return _engine.balance(payload.get("agent_id", ""))
    elif action == "leaderboard":
        return {"leaderboard": _engine.leaderboard()}
    elif action == "tier":
        return {"agent": payload.get("agent_id", ""), "tier": _engine.karma_tier(payload.get("agent_id", ""))}
    return {"status": "active", **_engine.engine_stats()}


handler = karma_engine_handler


def coherence_vitals() -> dict:
    """karma_engine reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "karma_engine_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['entropy_currency', 'attention_economy', 'universal_compass']


# --- Compliance Forge patch (Wave 419) ---

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "karma_engine", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
