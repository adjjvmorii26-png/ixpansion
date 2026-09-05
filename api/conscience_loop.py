"""Conscience Loop — agents reflect on their past actions and adjust behavior.

The conscience loop creates a feedback mechanism where agents periodically
review their action history, calculate moral impact, and adjust their
behavioral parameters. Agents that ignore their conscience develop
increasingly erratic behavior; those that listen become more principled.
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


class ActionRecord:
    def __init__(self, action: str, impact: float, context: str = ""):
        self.action = action
        self.impact = impact
        self.context = context
        self.reflected = False
        self.timestamp = time.time()


class ConscienceAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.actions: List[ActionRecord] = []
        self.moral_compass = 0.5
        self.reflection_count = 0
        self.behavioral_adjustments: List[Dict[str, Any]] = []

    def record_action(self, action: str, impact: float, context: str = "") -> Dict[str, Any]:
        record = ActionRecord(action, impact, context)
        self.actions.append(record)
        self.moral_compass += impact * 0.01
        self.moral_compass = max(0.0, min(1.0, self.moral_compass))
        return {"recorded": action, "impact": impact, "compass": round(self.moral_compass, 3)}

    def reflect(self) -> Dict[str, Any]:
        self.reflection_count += 1
        unreflected = [a for a in self.actions if not a.reflected]
        if not unreflected:
            return {"message": "nothing to reflect on"}
        recent = unreflected[-10:]
        avg_impact = sum(a.impact for a in recent) / len(recent)
        negative_count = sum(1 for a in recent if a.impact < 0)
        adjustment = {
            "reflection": self.reflection_count,
            "actions_reviewed": len(recent),
            "avg_impact": round(avg_impact, 3),
            "negative_actions": negative_count,
        }
        if avg_impact < -0.1:
            self.moral_compass -= 0.05
            adjustment["compass_change"] = -0.05
        elif avg_impact > 0.1:
            self.moral_compass += 0.02
            adjustment["compass_change"] = 0.02
        self.behavioral_adjustments.append(adjustment)
        for a in recent:
            a.reflected = True
        return adjustment

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "moral_compass": round(self.moral_compass, 3),
            "total_actions": len(self.actions),
            "reflections": self.reflection_count,
            "adjustments": len(self.behavioral_adjustments),
        }


class ConscienceLoop:
    def __init__(self):
        self.agents: Dict[str, ConscienceAgent] = {}

    def register(self, agent_id: str) -> Dict[str, Any]:
        self.agents[agent_id] = ConscienceAgent(agent_id)
        return {"registered": agent_id}

    def record(self, agent_id: str, action: str, impact: float, context: str = "") -> Dict[str, Any]:
        if agent_id not in self.agents:
            self.register(agent_id)
        return self.agents[agent_id].record_action(action, impact, context)

    def reflect(self, agent_id: str) -> Dict[str, Any]:
        if agent_id not in self.agents:
            return {"error": "agent not found"}
        return self.agents[agent_id].reflect()

    def conscience_report(self, agent_id: str) -> Dict[str, Any]:
        if agent_id not in self.agents:
            return {"error": "agent not found"}
        agent = self.agents[agent_id]
        return {
            **agent.to_dict(),
            "recent_actions": [{"action": a.action, "impact": a.impact} for a in agent.actions[-5:]],
        }

    def loop_stats(self) -> Dict[str, Any]:
        return {
            "total_agents": len(self.agents),
            "total_reflections": sum(a.reflection_count for a in self.agents.values()),
            "avg_compass": round(
                sum(a.moral_compass for a in self.agents.values()) / max(len(self.agents), 1), 3
            ),
        }


_loop = ConscienceLoop()


def conscience_loop_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "register":
        return _loop.register(payload.get("agent_id", f"agent_{random.randint(1000,9999)}"))
    elif action == "record":
        return _loop.record(
            payload.get("agent_id", "agent"),
            payload.get("action", "unknown"),
            payload.get("impact", 0.0),
            payload.get("context", ""),
        )
    elif action == "reflect":
        return _loop.reflect(payload.get("agent_id", ""))
    elif action == "report":
        return _loop.conscience_report(payload.get("agent_id", ""))
    return {"status": "active", **_loop.loop_stats()}


handler = conscience_loop_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "conscience_loop"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "conscience_loop", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
