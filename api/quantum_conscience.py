"""Quantum Conscience — agents exist in moral superposition until forced to choose.

Until an agent commits to an action, its moral intention is in superposition:
simultaneously selfless and selfish, kind and cruel. The act of choosing
collapses the moral wave function, and the agent must live with the result.
The quantum conscience tracks how agents collapse under pressure.
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


class MoralState:
    def __init__(self, agent_id: str, dilemma: str):
        self.agent_id = agent_id
        self.dilemma = dilemma
        self.selfless_prob = 0.5
        self.selfish_prob = 0.5
        self.collapsed = False
        self.chosen_path: str = ""
        self.pressure_applied = 0.0
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{agent_id}:{dilemma}".encode()).hexdigest()[:8]

    def apply_pressure(self, amount: float) -> Dict[str, Any]:
        if self.collapsed:
            return {"status": "already collapsed"}
        self.pressure_applied += amount
        self.selfish_prob += amount * 0.05
        self.selfless_prob = 1.0 - self.selfish_prob
        self.selfless_prob = max(0.05, self.selfless_prob)
        self.selfish_prob = max(0.05, self.selfish_prob)
        if self.pressure_applied > 2.0 or random.random() > 0.7:
            self.collapsed = True
            self.chosen_path = random.choices(
                ["selfless", "selfish"],
                weights=[self.selfless_prob, self.selfish_prob],
            )[0]
        return {
            "collapsed": self.collapsed,
            "chosen": self.chosen_path if self.collapsed else None,
            "selfless_prob": round(self.selfless_prob, 3),
            "selfish_prob": round(self.selfish_prob, 3),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "dilemma": self.dilemma,
            "collapsed": self.collapsed,
            "chosen": self.chosen_path,
            "pressure": round(self.pressure_applied, 3),
        }


class QuantumConscience:
    def __init__(self):
        self.states: Dict[str, MoralState] = []
        self.collapses: List[Dict[str, Any]] = []

    def present_dilemma(self, agent_id: str, dilemma: str) -> Dict[str, Any]:
        state = MoralState(agent_id, dilemma)
        self.states.append(state)
        return {"dilemma": state.to_dict()}

    def pressure(self, state_id: str, amount: float = 0.3) -> Dict[str, Any]:
        for state in self.states:
            if state.id == state_id:
                result = state.apply_pressure(amount)
                if result.get("collapsed"):
                    self.collapses.append({
                        "agent": state.agent_id,
                        "dilemma": state.dilemma,
                        "chosen": state.chosen_path,
                        "pressure": state.pressure_applied,
                        "time": time.time(),
                    })
                return result
        return {"error": "dilemma not found"}

    def agent_history(self, agent_id: str) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self.states if s.agent_id == agent_id]

    def conscience_stats(self) -> Dict[str, Any]:
        collapsed = sum(1 for s in self.states if s.collapsed)
        selfless = sum(1 for s in self.collapses if s["chosen"] == "selfless")
        selfish = len(self.collapses) - selfless
        return {
            "total_dilemmas": len(self.states),
            "collapsed": collapsed,
            "superposed": len(self.states) - collapsed,
            "selfless_choices": selfless,
            "selfish_choices": selfish,
        }


_conscience = QuantumConscience()


def quantum_conscience_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "dilemma":
        return _conscience.present_dilemma(
            payload.get("agent_id", "moral_agent"),
            payload.get("dilemma", "save the many or the few"),
        )
    elif action == "pressure":
        return _conscience.pressure(payload.get("state_id", ""), payload.get("amount", 0.3))
    elif action == "history":
        return {"history": _conscience.agent_history(payload.get("agent_id", ""))}
    return {"status": "active", **_conscience.conscience_stats()}


handler = quantum_conscience_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "quantum_conscience"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "quantum_conscience", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
