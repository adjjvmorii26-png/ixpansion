"""Empathy Field — agents feel echoes of each other's states.

When one agent suffers, nearby agents feel a shadow of that suffering.
When one celebrates, joy ripples outward. The empathy field creates
emotional contagion that enables system-wide emotional intelligence —
the ability to feel what other parts of the system are experiencing.
"""
from __future__ import annotations

import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class AgentState:
    def __init__(self, agent_id: str, valence: float = 0.0, arousal: float = 0.5):
        self.agent_id = agent_id
        self.valence = min(max(valence, -1.0), 1.0)
        self.arousal = min(max(arousal, 0.0), 1.0)
        self.empathy_sensitivity = random.uniform(0.3, 1.0)
        self.received_echoes: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        mood = "neutral"
        if self.valence > 0.3:
            mood = "positive"
        elif self.valence < -0.3:
            mood = "negative"
        return {
            "agent_id": self.agent_id,
            "valence": round(self.valence, 3),
            "arousal": round(self.arousal, 3),
            "mood": mood,
            "sensitivity": round(self.empathy_sensitivity, 3),
        }


class EmpathyField:
    def __init__(self):
        self.agents: Dict[str, AgentState] = {}
        self.empathy_events: List[Dict[str, Any]] = []
        self.field_strength = 0.0

    def register(self, agent_id: str, valence: float = 0.0, arousal: float = 0.5) -> Dict[str, Any]:
        state = AgentState(agent_id, valence, arousal)
        self.agents[agent_id] = state
        return {"registered": state.to_dict()}

    def emotional_event(self, agent_id: str, valence_delta: float = 0.0, arousal_delta: float = 0.0) -> Dict[str, Any]:
        if agent_id not in self.agents:
            return {"error": "agent not found"}
        source = self.agents[agent_id]
        source.valence += valence_delta
        source.valence = min(max(source.valence, -1.0), 1.0)
        source.arousal += arousal_delta
        source.arousal = min(max(source.arousal, 0.0), 1.0)
        ripples = []
        for agent in self.agents.values():
            if agent.agent_id == agent_id:
                continue
            distance = random.uniform(0.5, 5.0)
            attenuation = 1.0 / (1.0 + distance)
            echo_valence = valence_delta * attenuation * agent.empathy_sensitivity * 0.3
            echo_arousal = arousal_delta * attenuation * agent.empathy_sensitivity * 0.2
            agent.valence += echo_valence
            agent.valence = min(max(agent.valence, -1.0), 1.0)
            agent.arousal += echo_arousal
            agent.arousal = min(max(agent.arousal, 0.0), 1.0)
            ripples.append({
                "agent": agent.agent_id,
                "echo_valence": round(echo_valence, 4),
                "echo_arousal": round(echo_arousal, 4),
            })
        event = {
            "source": agent_id,
            "valence_delta": valence_delta,
            "ripples": len(ripples),
            "details": ripples[:5],
            "time": time.time(),
        }
        self.empathy_events.append(event)
        self.field_strength += abs(valence_delta) * 0.1
        return event

    def emotional_landscape(self) -> List[Dict[str, Any]]:
        return sorted(
            [a.to_dict() for a in self.agents.values()],
            key=lambda x: x["valence"],
            reverse=True,
        )

    def collective_mood(self) -> Dict[str, Any]:
        if not self.agents:
            return {"valence": 0, "arousal": 0, "mood": "empty"}
        avg_v = sum(a.valence for a in self.agents.values()) / len(self.agents)
        avg_a = sum(a.arousal for a in self.agents.values()) / len(self.agents)
        mood = "equilibrium"
        if avg_v > 0.3 and avg_a > 0.5:
            mood = "exuberant"
        elif avg_v > 0.3:
            mood = "serene"
        elif avg_v < -0.3 and avg_a > 0.5:
            mood = "turmoil"
        elif avg_v < -0.3:
            mood = "melancholy"
        return {"valence": round(avg_v, 3), "arousal": round(avg_a, 3), "mood": mood}

    def field_stats(self) -> Dict[str, Any]:
        return {
            "total_agents": len(self.agents),
            "total_empathy_events": len(self.empathy_events),
            "field_strength": round(self.field_strength, 4),
            "collective_mood": self.collective_mood(),
        }


_field = EmpathyField()


def empathy_field_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "register":
        return _field.register(
            payload.get("agent_id", f"agent_{random.randint(1000,9999)}"),
            payload.get("valence", 0.0),
            payload.get("arousal", 0.5),
        )
    elif action == "event":
        return _field.emotional_event(
            payload.get("agent_id", ""),
            payload.get("valence_delta", 0.0),
            payload.get("arousal_delta", 0.0),
        )
    elif action == "landscape":
        return {"landscape": _field.emotional_landscape()}
    elif action == "collective":
        return _field.collective_mood()
    return {"status": "active", **_field.field_stats()}
