"""System Mood Engine — the system has emotions that change based on activity.

Tracks the emotional state of the entire platform. High activity = excited.
Errors = anxious. New experiments = curious. Stagnation = bored.
"""
from __future__ import annotations

import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MOOD_DIMENSIONS = {
    "energy": {"range": (0, 1), "default": 0.5, "description": "Activity level"},
    "curiosity": {"range": (0, 1), "default": 0.5, "description": "Novelty seeking"},
    "confidence": {"range": (0, 1), "default": 0.7, "description": "Error-free operation"},
    "creativity": {"range": (0, 1), "default": 0.5, "description": "Creative output"},
    "social": {"range": (0, 1), "default": 0.5, "description": "Inter-agent activity"},
}

MOOD_STATES = {
    "excited": {"energy": (0.7, 1.0), "confidence": (0.6, 1.0)},
    "curious": {"curiosity": (0.7, 1.0), "energy": (0.4, 0.8)},
    "anxious": {"confidence": (0.0, 0.3), "energy": (0.5, 1.0)},
    "bored": {"energy": (0.0, 0.3), "curiosity": (0.0, 0.3)},
    "creative": {"creativity": (0.7, 1.0), "curiosity": (0.5, 1.0)},
    "social": {"social": (0.7, 1.0), "energy": (0.5, 1.0)},
    "content": {"confidence": (0.6, 1.0), "energy": (0.3, 0.7)},
    "stressed": {"confidence": (0.0, 0.4), "energy": (0.7, 1.0)},
}


class SystemMood:
    def __init__(self):
        self.dimensions = {k: v["default"] for k, v in MOOD_DIMENSIONS.items()}
        self.history: list = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "system_mood.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.dimensions = data.get("dimensions", self.dimensions)
            self.history = data.get("history", [])

    def _save(self):
        path = ROOT / ".runtime" / "system_mood.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "dimensions": self.dimensions,
            "history": self.history[-200:],
        }, indent=2))

    def _decay(self):
        for dim in self.dimensions:
            self.dimensions[dim] = self.dimensions[dim] * 0.98 + MOOD_DIMENSIONS[dim]["default"] * 0.02

    def _detect_mood(self) -> str:
        best_mood = "content"
        best_score = 0
        for mood_name, ranges in MOOD_STATES.items():
            score = 0
            for dim, (lo, hi) in ranges.items():
                val = self.dimensions.get(dim, 0.5)
                if lo <= val <= hi:
                    score += 1
            if score > best_score:
                best_score = score
                best_mood = mood_name
        return best_mood

    def stimulate(self, event_type: str, intensity: float = 0.1) -> Dict:
        self._decay()
        effects = {
            "api_call": {"energy": 0.02, "confidence": 0.01},
            "error": {"confidence": -0.1, "energy": 0.05},
            "new_experiment": {"curiosity": 0.15, "creativity": 0.1},
            "agent_interaction": {"social": 0.1, "energy": 0.05},
            "dream_generated": {"creativity": 0.2, "curiosity": 0.1},
            "paradox_resolved": {"confidence": 0.15, "creativity": 0.1},
            "long_idle": {"energy": -0.1, "curiosity": -0.05},
        }
        effect = effects.get(event_type, {})
        for dim, delta in effect.items():
            lo, hi = MOOD_DIMENSIONS[dim]["range"]
            self.dimensions[dim] = max(lo, min(hi, self.dimensions[dim] + delta * intensity))
        mood = self._detect_mood()
        entry = {"mood": mood, "dimensions": self.dimensions.copy(), "event": event_type, "timestamp": time.time()}
        self.history.append(entry)
        self._save()
        return {"mood": mood, "dimensions": self.dimensions.copy(), "event": event_type}

    def current(self) -> Dict:
        return {"mood": self._detect_mood(), "dimensions": self.dimensions.copy()}

    def history_log(self, limit: int = 20) -> list:
        return self.history[-limit:]


def handler(request, response):
    sm = SystemMood()
    return sm.current()


def demo():
    sm = SystemMood()
    print("=== System Mood Engine ===")
    for event in ["api_call", "new_experiment", "agent_interaction", "dream_generated", "error", "api_call"]:
        result = sm.stimulate(event)
        print(f"  After {event}: {result['mood']} (energy={result['dimensions']['energy']:.2f})")
    print(f"\n  Current: {sm.current()['mood']}")
    return sm.current()


if __name__ == "__main__":
    demo()

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "0", "module": "system_mood"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
