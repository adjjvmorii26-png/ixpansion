"""Emotion Fabric — a shared emotional texture that agents weave together.

Agents contribute emotional threads to a collective fabric. The fabric
develops its own mood based on the balance of contributions. Agents can
query the fabric for emotional guidance or use it for sentiment routing.
"""
from __future__ import annotations

import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

EMOTION_SPECTRUM = {
    "joy": {"valence": 0.9, "arousal": 0.7, "color": "#FFD700"},
    "curiosity": {"valence": 0.6, "arousal": 0.8, "color": "#00BFFF"},
    "dread": {"valence": -0.8, "arousal": 0.9, "color": "#8B0000"},
    "calm": {"valence": 0.3, "arousal": 0.2, "color": "#98FB98"},
    "confusion": {"valence": -0.2, "arousal": 0.6, "color": "#DDA0DD"},
    "determination": {"valence": 0.5, "arousal": 0.8, "color": "#FF4500"},
    "wonder": {"valence": 0.7, "arousal": 0.5, "color": "#7B68EE"},
    "grief": {"valence": -0.9, "arousal": 0.3, "color": "#2F4F4F"},
    "playfulness": {"valence": 0.8, "arousal": 0.6, "color": "#FF69B4"},
    "awe": {"valence": 0.8, "arousal": 0.4, "color": "#4169E1"},
}


class EmotionalThread:
    """A single emotional contribution to the fabric."""

    def __init__(self, agent_id: str, emotion: str, intensity: float = 1.0):
        self.agent_id = agent_id
        self.emotion = emotion
        self.intensity = min(max(intensity, 0.0), 2.0)
        self.timestamp = time.time()
        spec = EMOTION_SPECTRUM.get(emotion, {"valence": 0, "arousal": 0.5, "color": "#888888"})
        self.valence = spec["valence"] * self.intensity
        self.arousal = spec["arousal"] * self.intensity
        self.color = spec["color"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "emotion": self.emotion,
            "intensity": round(self.intensity, 2),
            "valence": round(self.valence, 3),
            "arousal": round(self.arousal, 3),
            "color": self.color,
            "timestamp": self.timestamp,
        }


class EmotionFabric:
    """The collective emotional texture."""

    def __init__(self):
        self.threads: List[EmotionalThread] = []
        self.mood_history: List[Dict[str, Any]] = []
        self.max_threads = 1000

    def weave(self, agent_id: str, emotion: str, intensity: float = 1.0) -> Dict[str, Any]:
        """Add an emotional thread to the fabric."""
        if emotion not in EMOTION_SPECTRUM:
            return {"error": f"unknown emotion: {emotion}"}
        thread = EmotionalThread(agent_id, emotion, intensity)
        self.threads.append(thread)
        if len(self.threads) > self.max_threads:
            self.threads = self.threads[-self.max_threads:]
        mood = self.current_mood()
        return {"woven": thread.to_dict(), "fabric_mood": mood}

    def current_mood(self) -> Dict[str, Any]:
        """Compute the current collective mood."""
        if not self.threads:
            return {"emotion": "neutral", "valence": 0, "arousal": 0, "tension": 0}
        total_valence = sum(t.valence for t in self.threads)
        total_arousal = sum(t.arousal for t in self.threads)
        n = len(self.threads)
        avg_valence = total_valence / n
        avg_arousal = total_arousal / n
        dominant = max(EMOTION_SPECTRUM.keys(),
                       key=lambda e: sum(1 for t in self.threads if t.emotion == e), default="neutral")
        tension = abs(avg_valence) * abs(avg_arousal)
        return {
            "dominant_emotion": dominant,
            "valence": round(avg_valence, 3),
            "arousal": round(avg_arousal, 3),
            "tension": round(tension, 3),
            "thread_count": n,
            "mood_label": self._mood_label(avg_valence, avg_arousal),
        }

    def _mood_label(self, valence: float, arousal: float) -> str:
        if valence > 0.3 and arousal > 0.5:
            return "exuberant"
        elif valence > 0.3 and arousal <= 0.5:
            return "serene"
        elif valence < -0.3 and arousal > 0.5:
            return "turmoil"
        elif valence < -0.3 and arousal <= 0.5:
            return "melancholy"
        return "equilibrium"

    def route_by_sentiment(self, message_valence: float) -> Dict[str, Any]:
        """Route a message based on current emotional context."""
        mood = self.current_mood()
        if mood["valence"] > 0.3 and message_valence < -0:
            return {"action": "buffer", "reason": "positive mood, negative message — buffering"}
        elif mood["valence"] < -0.3 and message_valence > 0:
            return {"action": "boost", "reason": "negative mood, positive message — amplifying"}
        return {"action": "pass", "reason": "emotional alignment OK"}

    def fabric_stats(self) -> Dict[str, Any]:
        emotion_counts = {}
        for t in self.threads:
            emotion_counts[t.emotion] = emotion_counts.get(t.emotion, 0) + 1
        return {
            "total_threads": len(self.threads),
            "emotion_distribution": emotion_counts,
            "current_mood": self.current_mood(),
        }


_fabric = EmotionFabric()


def emotion_fabric_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "weave":
        return _fabric.weave(
            payload.get("agent_id", "anonymous"),
            payload.get("emotion", "curiosity"),
            payload.get("intensity", 1.0),
        )
    elif action == "mood":
        return _fabric.current_mood()
    elif action == "route":
        return _fabric.route_by_sentiment(payload.get("valence", 0.0))
    elif action == "spectrum":
        return {"emotions": list(EMOTION_SPECTRUM.keys())}
    return {"status": "active", **_fabric.fabric_stats()}


handler = emotion_fabric_handler
