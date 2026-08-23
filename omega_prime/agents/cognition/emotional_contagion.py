"""Emotional contagion network — moods spread through proximity.

Each agent carries an emotional state (valence: -1 to +1, arousal: 0-1).
When agents are near each other, emotions transfer with strength inversely
proportional to distance. High-arousal emotions spread faster. Cascading
panic or euphoria can ripple through populations.

Emotions influence behavior: high negative valence reduces cooperation;
high arousal increases action frequency but decreases accuracy.
"""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EmotionalState:
    valence: float = 0.0       # -1 (miserable) to +1 (euphoric)
    arousal: float = 0.3       # 0 (calm) to 1 (frenzied)
    dominant_emotion: str = "neutral"

    @property
    def is_contagious(self) -> bool:
        """High-arousal emotions spread more easily."""
        return abs(self.valence) > 0.4 or self.arousal > 0.6

    def classify(self) -> str:
        if self.valence > 0.5 and self.arousal > 0.7:
            return "ecstatic"
        elif self.valence > 0.3:
            return "content"
        elif self.valence < -0.5 and self.arousal > 0.7:
            return "panicked"
        elif self.valence < -0.3:
            return "distressed"
        elif self.arousal > 0.8:
            return "agitated"
        return "neutral"


class EmotionalContagionNetwork:
    TRANSFER_RADIUS = 5.0
    TRANSFER_RATE = 0.15
    DECAY_RATE = 0.02

    def __init__(self) -> None:
        self._states: dict[str, EmotionalState] = {}
        self._positions: dict[str, tuple[float, float]] = {}
        self._cascade_log: list[dict[str, Any]] = []

    def set_emotion(self, agent_id: str, valence: float, arousal: float) -> None:
        state = EmotionalState(
            valence=max(-1.0, min(1.0, valence)),
            arousal=max(0.0, min(1.0, arousal)),
        )
        state.dominant_emotion = state.classify()
        self._states[agent_id] = state

    def set_position(self, agent_id: str, pos: tuple[float, float]) -> None:
        self._positions[agent_id] = pos

    def propagate(self) -> list[dict[str, Any]]:
        """One propagation pass: emotions transfer between near agents."""
        transfers = []
        agents = list(self._states.keys())

        for i, source_id in enumerate(agents):
            source = self._states[source_id]
            if not source.is_contagious:
                continue

            source_pos = self._positions.get(source_id)
            if not source_pos:
                continue

            for target_id in agents[i+1:]:
                target_pos = self._positions.get(target_id)
                if not target_pos:
                    continue

                dist = math.hypot(
                    source_pos[0] - target_pos[0],
                    source_pos[1] - target_pos[1]
                )
                if dist > self.TRANSFER_RADIUS:
                    continue

                target = self._states.get(target_id)
                if not target:
                    continue

                # Transfer strength falls off with distance; arousal amplifies
                falloff = math.exp(-dist / self.TRANSFER_RADIUS)
                strength = self.TRANSFER_RATE * falloff * source.arousal

                # Transfer valence and arousal
                old_v = target.valence
                target.valence += (source.valence - old_v) * strength
                target.arousal += (source.arousal - target.arousal) * strength * 0.7
                target.valence = max(-1.0, min(1.0, target.valence))
                target.arousal = max(0.0, min(1.0, target.arousal))
                target.dominant_emotion = target.classify()

                if abs(target.valence - old_v) > 0.01:
                    transfers.append({
                        "from": source_id[:8], "to": target_id[:8],
                        "emotion": source.dominant_emotion,
                        "strength": round(strength, 4),
                        "target_shift": round(target.valence - old_v, 4),
                    })

        return transfers

    def tick(self) -> dict[str, Any]:
        """Natural decay + propagation."""
        for state in self._states.values():
            state.valence *= (1.0 - self.DECAY_RATE)
            state.arousal += (0.3 - state.arousal) * self.DECAY_RATE
            state.dominant_emotion = state.classify()

        transfers = self.propagate()

        mood_dist = defaultdict(int)
        for s in self._states.values():
            mood_dist[s.dominant_emotion] += 1

        avg_valence = sum(s.valence for s in self._states.values()) / max(len(self._states), 1)

        result = {
            "transfers_this_tick": len(transfers),
            "mood_distribution": dict(mood_dist),
            "avg_valence": round(avg_valence, 4),
        }

        if len(transfers) >= 5:
            self._cascade_log.append({
                "size": len(transfers), "avg_valence": round(avg_valence, 4),
            })
            result["cascade_detected"] = True

        return result

    @property
    def emotional_weather(self) -> dict[str, Any]:
        """Aggregate emotional climate of the population."""
        states = list(self._states.values())
        if not states:
            return {"climate": "empty"}
        avg_v = sum(s.valence for s in states) / len(states)
        avg_a = sum(s.arousal for s in states) / len(states)
        if avg_v > 0.2 and avg_a < 0.5:
            climate = "serene"
        elif avg_v > 0.2:
            climate = "jubilant"
        elif avg_v < -0.2 and avg_a > 0.6:
            climate = "riot"
        elif avg_v < -0.2:
            climate = "somber"
        else:
            climate = "calm"
        return {
            "climate": climate,
            "valence": round(avg_v, 4),
            "arousal": round(avg_a, 4),
            "population": len(states),
        }
