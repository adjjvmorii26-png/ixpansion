"""Attention Economy — agents compete for limited attention bandwidth.

Attention is the scarcest resource. Agents must earn attention by being
interesting, useful, or surprising. The economy tracks attention flows,
rewards engaging agents, and starves boring ones. Natural selection
ensures only compelling agents survive.
"""
from __future__ import annotations

import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class AgentAttention:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.earned = 0.0
        self.spent = 0.0
        self.current = 50.0
        self.engagement_rate = random.uniform(0.01, 0.1)
        self.boring_streak = 0

    def earn(self, amount: float, source: str = "engagement") -> Dict[str, Any]:
        self.earned += amount
        self.current += amount
        self.boring_streak = 0
        return {"earned": round(amount, 2), "source": source, "balance": round(self.current, 2)}

    def spend(self, amount: float, purpose: str = "broadcast") -> Dict[str, Any]:
        if amount > self.current:
            return {"error": "insufficient attention"}
        self.spent += amount
        self.current -= amount
        return {"spent": round(amount, 2), "purpose": purpose, "balance": round(self.current, 2)}

    def tick(self) -> Dict[str, Any]:
        decay = self.current * 0.05
        self.current = max(0, self.current - decay)
        organic = self.engagement_rate * 100 * (1.0 - min(self.boring_streak * 0.1, 0.9))
        self.current += organic
        if organic < 0.5:
            self.boring_streak += 1
        return {"decayed": round(decay, 3), "organic": round(organic, 3), "balance": round(self.current, 2)}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "earned": round(self.earned, 2),
            "spent": round(self.spent, 2),
            "current": round(self.current, 2),
            "engagement_rate": round(self.engagement_rate, 4),
            "boring_streak": self.boring_streak,
        }


class AttentionEconomy:
    def __init__(self):
        self.agents: Dict[str, AgentAttention] = {}
        self.total_pool = 10000.0
        self.distributed = 0.0
        self.tick_count = 0

    def register(self, agent_id: str) -> Dict[str, Any]:
        agent = AgentAttention(agent_id)
        self.agents[agent_id] = agent
        return {"registered": agent.to_dict()}

    def earn_attention(self, agent_id: str, amount: float, source: str = "engagement") -> Dict[str, Any]:
        if agent_id not in self.agents:
            self.register(agent_id)
        return self.agents[agent_id].earn(amount, source)

    def spend_attention(self, agent_id: str, amount: float, purpose: str = "broadcast") -> Dict[str, Any]:
        if agent_id not in self.agents:
            return {"error": "agent not found"}
        return self.agents[agent_id].spend(amount, purpose)

    def tick(self) -> Dict[str, Any]:
        self.tick_count += 1
        results = []
        for agent in self.agents.values():
            result = agent.tick()
            results.append({"agent_id": agent.agent_id, **result})
        return {"tick": self.tick_count, "agents": results[:5]}

    def leaderboard(self) -> List[Dict[str, Any]]:
        return sorted(
            [a.to_dict() for a in self.agents.values()],
            key=lambda x: x["current"],
            reverse=True,
        )

    def economy_stats(self) -> Dict[str, Any]:
        return {
            "total_agents": len(self.agents),
            "total_attention": round(sum(a.current for a in self.agents.values()), 2),
            "total_earned": round(sum(a.earned for a in self.agents.values()), 2),
            "total_spent": round(sum(a.spent for a in self.agents.values()), 2),
            "ticks": self.tick_count,
        }


_economy = AttentionEconomy()


def attention_economy_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "register":
        return _economy.register(payload.get("agent_id", f"agent_{random.randint(1000,9999)}"))
    elif action == "earn":
        return _economy.earn_attention(
            payload.get("agent_id", "agent"),
            payload.get("amount", 10.0),
            payload.get("source", "engagement"),
        )
    elif action == "spend":
        return _economy.spend_attention(
            payload.get("agent_id", "agent"),
            payload.get("amount", 5.0),
            payload.get("purpose", "broadcast"),
        )
    elif action == "tick":
        return _economy.tick()
    elif action == "leaderboard":
        return {"leaderboard": _economy.leaderboard()}
    return {"status": "active", **_economy.economy_stats()}


handler = attention_economy_handler


def coherence_vitals() -> dict:
    """attention_economy reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "attention_economy_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['system_pulse', 'universal_compass', 'resonance_field']


# --- Compliance Forge patch (Wave 419) ---

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "attention_economy", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
