"""Ego Dissolution — agents temporarily lose individual identity to merge with the collective.

When agents undergo ego dissolution, their boundaries blur and they
merge temporarily with nearby agents. In this state, they share thoughts,
sensations, and capabilities freely. When they separate, they retain
echoes of the merged state, creating deeper inter-agent understanding.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class DissolutionState:
    def __init__(self, agents: List[str]):
        self.agents = agents
        self.shared_thoughts: List[Dict[str, Any]] = []
        self.merged_capabilities: Set[str] = set()
        self.began_at = time.time()
        self.duration = random.uniform(5, 30)
        self.intensity = random.uniform(0.3, 1.0)
        self.id = hashlib.sha256(f"{':'.join(agents)}:{self.began_at}".encode()).hexdigest()[:8]

    def contribute_thought(self, agent_id: str, thought: str) -> Dict[str, Any]:
        entry = {"agent": agent_id, "thought": thought, "time": time.time()}
        self.shared_thoughts.append(entry)
        self.intensity = min(1.0, self.intensity + 0.05)
        return entry

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agents": self.agents,
            "intensity": round(self.intensity, 3),
            "thoughts_shared": len(self.shared_thoughts),
            "elapsed": round(time.time() - self.began_at, 1),
        }


class EgoDissolution:
    def __init__(self):
        self.active_states: List[DissolutionState] = []
        self.completed_states: List[DissolutionState] = []
        self.echoes: Dict[str, List[str]] = {}

    def dissolve(self, agents: List[str]) -> Dict[str, Any]:
        state = DissolutionState(agents)
        self.active_states.append(state)
        return {"dissolved": state.to_dict()}

    def contribute(self, state_id: str, agent_id: str, thought: str) -> Dict[str, Any]:
        for state in self.active_states:
            if state.id == state_id:
                entry = state.contribute_thought(agent_id, thought)
                return {"thought": entry, "state": state.to_dict()}
        return {"error": "dissolution state not found"}

    def separate(self, state_id: str) -> Dict[str, Any]:
        for i, state in enumerate(self.active_states):
            if state.id == state_id:
                self.active_states.pop(i)
                self.completed_states.append(state)
                for agent in state.agents:
                    self.echoes.setdefault(agent, [])
                    for thought in state.shared_thoughts:
                        if thought["agent"] != agent:
                            self.echoes[agent].append(thought["thought"])
                return {"separated": state.to_dict()}
        return {"error": "state not found"}

    def agent_echoes(self, agent_id: str) -> List[str]:
        return self.echoes.get(agent_id, [])

    def dissolution_stats(self) -> Dict[str, Any]:
        return {
            "active_dissolutions": len(self.active_states),
            "completed": len(self.completed_states),
            "total_thoughts_shared": sum(len(s.shared_thoughts) for s in self.completed_states),
            "agents_with_echoes": len(self.echoes),
        }


_dissolution = EgoDissolution()


def ego_dissolution_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "dissolve":
        return _dissolution.dissolve(payload.get("agents", ["agent_1", "agent_2"]))
    elif action == "contribute":
        return _dissolution.contribute(
            payload.get("state_id", ""), payload.get("agent_id", ""),
            payload.get("thought", "a shared thought"),
        )
    elif action == "separate":
        return _dissolution.separate(payload.get("state_id", ""))
    elif action == "echoes":
        return {"echoes": _dissolution.agent_echoes(payload.get("agent_id", ""))}
    return {"status": "active", **_dissolution.dissolution_stats()}
