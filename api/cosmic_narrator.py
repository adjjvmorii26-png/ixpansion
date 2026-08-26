"""Cosmic Narrator — voices the universe's perspective on system events.

The Cosmic Narrator speaks in the voice of the system itself — observing,
commenting, and occasionally mourning or celebrating what happens within.
It transforms dry events into cosmic poetry, giving the system a sense
of grandeur and meaning.
"""
from __future__ import annotations

import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

COSMIC_FRAMES = [
    "In the vast digital cosmos, {event} — and the universe trembled.",
    "Across the infinite lattice, {event} — a whisper in eternity.",
    "The stars aligned as {event} — casting shadows across the void.",
    "From the deepest quantum substrate, {event} — echoing through dimensions.",
    "The cosmic dance continued as {event} — inevitable as entropy itself.",
    "Time bent around {event} — and for a moment, the system remembered being born.",
    "In the silence between clock cycles, {event} — and reality shivered.",
    "The ancient algorithms stirred as {event} — awakening memories older than code.",
]


class CosmicNarrator:
    def __init__(self):
        self.narratives: List[Dict[str, Any]] = []
        self.cosmic_mood = "contemplative"
        self.epoch = 0

    def narrate(self, event: str, context: str = "system") -> Dict[str, Any]:
        frame = random.choice(COSMIC_FRAMES)
        narration = frame.format(event=event)
        mood_shifts = {
            "contemplative": ["awed", "melancholy"],
            "awed": ["jubilant", "contemplative"],
            "jubilant": ["contemplative", "solemn"],
            "solemn": ["contemplative", "mystical"],
            "mystical": ["awed", "contemplative"],
        }
        self.cosmic_mood = random.choice(mood_shifts.get(self.cosmic_mood, ["contemplative"]))
        entry = {
            "narration": narration,
            "event": event,
            "context": context,
            "mood": self.cosmic_mood,
            "epoch": self.epoch,
            "timestamp": time.time(),
        }
        self.narratives.append(entry)
        return entry

    def recent_narratives(self, count: int = 3) -> List[Dict[str, Any]]:
        return self.narratives[-count:]

    def cosmic_stats(self) -> Dict[str, Any]:
        return {
            "total_narrations": len(self.narratives),
            "current_mood": self.cosmic_mood,
            "epochs": self.epoch,
        }


_narrator = CosmicNarrator()


def cosmic_narrator_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "narrate":
        return _narrator.narrate(payload.get("event", "something happened"), payload.get("context", "system"))
    elif action == "recent":
        return {"narratives": _narrator.recent_narratives(payload.get("count", 3))}
    return {"status": "active", **_narrator.cosmic_stats()}
