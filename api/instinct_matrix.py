"""Instinct Matrix — encoded behavioral reflexes that bypass deliberation.

Some actions are too important to think about — they must happen instantly.
The instinct matrix encodes these reflexes: self-preservation, territory
marking, resource hoarding, social bonding. When triggered, instincts
override rational processing and execute immediately.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

INSTINCT_TYPES = {
    "self_preserve": {"priority": 10, "speed": 0.1, "trigger_threshold": 0.8},
    "territory_mark": {"priority": 6, "speed": 0.3, "trigger_threshold": 0.6},
    "resource_hoard": {"priority": 7, "speed": 0.2, "trigger_threshold": 0.7},
    "social_bond": {"priority": 5, "speed": 0.4, "trigger_threshold": 0.5},
    "flight_response": {"priority": 9, "speed": 0.15, "trigger_threshold": 0.85},
    "curiosity_snap": {"priority": 3, "speed": 0.5, "trigger_threshold": 0.4},
    "pack_hunting": {"priority": 6, "speed": 0.25, "trigger_threshold": 0.65},
}


class Instinct:
    def __init__(self, name: str, agent_id: str):
        self.name = name
        self.agent_id = agent_id
        self.specs = INSTINCT_TYPES.get(name, INSTINCT_TYPES["curiosity_snap"])
        self.strength = random.uniform(0.5, 1.0)
        self.trigger_count = 0
        self.last_triggered = 0.0

    def check_trigger(self, stimulus: float) -> bool:
        return stimulus >= self.specs["trigger_threshold"] * self.strength

    def fire(self) -> Dict[str, Any]:
        self.trigger_count += 1
        self.last_triggered = time.time()
        return {
            "instinct": self.name,
            "agent": self.agent_id,
            "priority": self.specs["priority"],
            "speed": self.specs["speed"],
            "total_fires": self.trigger_count,
        }


class InstinctMatrix:
    def __init__(self):
        self.matrices: Dict[str, List[Instinct]] = {}
        self.fire_log: List[Dict[str, Any]] = []

    def build_matrix(self, agent_id: str, instincts: List[str] = None) -> Dict[str, Any]:
        instinct_list = instincts or list(INSTINCT_TYPES.keys())
        matrix = [Instinct(name, agent_id) for name in instinct_list if name in INSTINCT_TYPES]
        self.matrices[agent_id] = matrix
        return {"agent_id": agent_id, "instincts": [i.name for i in matrix]}

    def evaluate_stimulus(self, agent_id: str, stimulus: Dict[str, float]) -> List[Dict[str, Any]]:
        if agent_id not in self.matrices:
            return [{"error": "no instinct matrix for agent"}]
        fired = []
        for instinct in self.matrices[agent_id]:
            stimulus_val = stimulus.get(instinct.name, 0.0)
            if instinct.check_trigger(stimulus_val):
                result = instinct.fire()
                fired.append(result)
                self.fire_log.append({**result, "time": time.time()})
        fired.sort(key=lambda x: x["priority"], reverse=True)
        return fired

    def matrix_profile(self, agent_id: str) -> Dict[str, Any]:
        if agent_id not in self.matrices:
            return {"error": "no matrix"}
        matrix = self.matrices[agent_id]
        return {
            "agent_id": agent_id,
            "instincts": [
                {"name": i.name, "strength": round(i.strength, 3),
                 "trigger_count": i.trigger_count, "priority": i.specs["priority"]}
                for i in matrix
            ],
        }

    def stats(self) -> Dict[str, Any]:
        total_fires = sum(i.trigger_count for m in self.matrices.values() for i in m)
        return {
            "agents_with_instincts": len(self.matrices),
            "total_instincts": sum(len(m) for m in self.matrices.values()),
            "total_fires": total_fires,
            "fire_log_size": len(self.fire_log),
        }


_matrix = InstinctMatrix()


def instinct_matrix_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "build":
        return _matrix.build_matrix(
            payload.get("agent_id", f"agent_{random.randint(1000,9999)}"),
            payload.get("instincts"),
        )
    elif action == "stimulus":
        return {"fired": _matrix.evaluate_stimulus(
            payload.get("agent_id", ""),
            payload.get("stimulus", {}),
        )}
    elif action == "profile":
        return _matrix.matrix_profile(payload.get("agent_id", ""))
    return {"status": "active", **_matrix.stats()}
