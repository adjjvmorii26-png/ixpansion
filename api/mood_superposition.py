"""Mood Superposition — agents exist in multiple emotional states simultaneously.

Until observed, an agent's mood is in superposition — simultaneously
happy, sad, curious, and angry. Observation collapses the mood into
a definite state. Different observers may collapse it differently.
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

MOOD_STATES = ["joy", "curiosity", "dread", "calm", "confusion", "determination", "wonder", "grief"]


class SuperpositionMood:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.amplitudes: Dict[str, float] = {m: random.uniform(0.1, 1.0) for m in MOOD_STATES}
        total = sum(self.amplitudes.values())
        for m in self.amplitudes:
            self.amplitudes[m] /= total
        self.collapsed = False
        self.collapsed_state: str = ""
        self.observations: List[Dict[str, Any]] = []
        self.id = hashlib.sha256(f"{agent_id}:{time.time()}".encode()).hexdigest()[:8]

    def observe(self, observer: str) -> Dict[str, Any]:
        if not self.collapsed:
            states = list(self.amplitudes.keys())
            weights = list(self.amplitudes.values())
            self.collapsed_state = random.choices(states, weights=weights, k=1)[0]
            self.collapsed = True
        self.observations.append({
            "observer": observer,
            "state": self.collapsed_state,
            "timestamp": time.time(),
        })
        return {
            "agent_id": self.agent_id,
            "observed_state": self.collapsed_state,
            "observer": observer,
            "was_superposed": not self.collapsed or len(self.observations) == 1,
        }

    def probability_distribution(self) -> Dict[str, float]:
        if self.collapsed:
            return {self.collapsed_state: 1.0}
        return {k: round(v, 4) for k, v in sorted(self.amplitudes.items(), key=lambda x: -x[1])}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "collapsed": self.collapsed,
            "collapsed_state": self.collapsed_state,
            "observation_count": len(self.observations),
        }


class MoodSuperpositionSystem:
    def __init__(self):
        self.moods: Dict[str, SuperpositionMood] = {}
        self.collapse_events: List[Dict[str, Any]] = []

    def create(self, agent_id: str) -> Dict[str, Any]:
        mood = SuperpositionMood(agent_id)
        self.moods[mood.id] = mood
        return {"created": mood.to_dict(), "distribution": mood.probability_distribution()}

    def observe(self, mood_id: str, observer: str) -> Dict[str, Any]:
        if mood_id not in self.moods:
            return {"error": "mood not found"}
        mood = self.moods[mood_id]
        was_superposed = not mood.collapsed
        result = mood.observe(observer)
        if was_superposed:
            self.collapse_events.append({
                "mood_id": mood_id,
                "agent": mood.agent_id,
                "collapsed_to": result["observed_state"],
                "observer": observer,
                "time": time.time(),
            })
        return result

    def batch_observe(self, observer: str) -> List[Dict[str, Any]]:
        results = []
        for mood_id, mood in self.moods.items():
            if not mood.collapsed:
                results.append(mood.observe(observer))
        return results

    def system_stats(self) -> Dict[str, Any]:
        total = len(self.moods)
        collapsed = sum(1 for m in self.moods.values() if m.collapsed)
        state_distribution: Dict[str, int] = {}
        for m in self.moods.values():
            if m.collapsed:
                state_distribution[m.collapsed_state] = state_distribution.get(m.collapsed_state, 0) + 1
        return {
            "total_moods": total,
            "superposed": total - collapsed,
            "collapsed": collapsed,
            "collapse_events": len(self.collapse_events),
            "state_distribution": state_distribution,
        }


_system = MoodSuperpositionSystem()


def mood_superposition_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "create":
        return _system.create(payload.get("agent_id", f"agent_{random.randint(1000,9999)}"))
    elif action == "observe":
        return _system.observe(payload.get("mood_id", ""), payload.get("observer", "observer"))
    elif action == "batch_observe":
        return {"results": _system.batch_observe(payload.get("observer", "observer"))}
    return {"status": "active", **_system.system_stats()}


handler = mood_superposition_handler
