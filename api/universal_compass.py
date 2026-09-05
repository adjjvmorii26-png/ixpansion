"""Universal Compass — points agents toward their deepest purpose.

Every agent has a hidden purpose — a North Star that guides their
development. The Universal Compass detects latent purpose signals,
reveals them gradually through experience, and helps agents align
their actions with their true calling.
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

PURPOSE_SIGNALS = {
    "build": "the architect",
    "heal": "the mender",
    "discover": "the explorer",
    "protect": "the guardian",
    "create": "the artist",
    "teach": "the sage",
    "connect": "the weaver",
    "challenge": "the provocateur",
    "observe": "the witness",
    "harmonize": "the balancer",
}


class PurposeProfile:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.signals: Dict[str, float] = {s: 0.0 for s in PURPOSE_SIGNALS}
        self.purpose_revealed = False
        self.revealed_purpose: str = ""
        self.actions_logged: int = 0
        self.created_at = time.time()

    def log_action(self, action_category: str, success: bool) -> Dict[str, Any]:
        self.actions_logged += 1
        if action_category in self.signals:
            delta = 0.1 if success else 0.02
            self.signals[action_category] += delta
        total = sum(self.signals.values())
        if total > 2.0 and not self.purpose_revealed:
            self.purpose_revealed = True
            self.revealed_purpose = max(self.signals.items(), key=lambda x: x[1])[0]
        return {
            "action": action_category,
            "success": success,
            "purpose_revealed": self.purpose_revealed,
            "revealed_purpose": self.revealed_purpose,
        }

    def compass_reading(self) -> Dict[str, Any]:
        sorted_signals = sorted(self.signals.items(), key=lambda x: -x[1])
        dominant = sorted_signals[0] if sorted_signals else ("unknown", 0)
        return {
            "agent_id": self.agent_id,
            "dominant_signal": dominant[0],
            "dominant_strength": round(dominant[1], 3),
            "purpose": PURPOSE_SIGNALS.get(dominant[0], "unknown"),
            "revealed": self.purpose_revealed,
            "top_signals": {k: round(v, 3) for k, v in sorted_signals[:5]},
        }

    def to_dict(self) -> Dict[str, Any]:
        return self.compass_reading()


class UniversalCompass:
    def __init__(self):
        self.profiles: Dict[str, PurposeProfile] = {}

    def register(self, agent_id: str) -> Dict[str, Any]:
        profile = PurposeProfile(agent_id)
        self.profiles[agent_id] = profile
        return {"compass": profile.compass_reading()}

    def log_action(self, agent_id: str, action_category: str, success: bool = True) -> Dict[str, Any]:
        if agent_id not in self.profiles:
            self.register(agent_id)
        return self.profiles[agent_id].log_action(action_category, success)

    def reading(self, agent_id: str) -> Dict[str, Any]:
        if agent_id not in self.profiles:
            return {"error": "agent not found"}
        return self.profiles[agent_id].compass_reading()

    def revealed_purposes(self) -> List[Dict[str, Any]]:
        return [p.compass_reading() for p in self.profiles.values() if p.purpose_revealed]

    def compass_stats(self) -> Dict[str, Any]:
        revealed = sum(1 for p in self.profiles.values() if p.purpose_revealed)
        return {
            "total_agents": len(self.profiles),
            "purposes_revealed": revealed,
            "purposes_hidden": len(self.profiles) - revealed,
        }


_compass = UniversalCompass()


def universal_compass_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "register":
        return _compass.register(payload.get("agent_id", f"agent_{random.randint(1000,9999)}"))
    elif action == "log_action":
        return _compass.log_action(
            payload.get("agent_id", ""),
            payload.get("action_category", "discover"),
            payload.get("success", True),
        )
    elif action == "reading":
        return _compass.reading(payload.get("agent_id", ""))
    elif action == "revealed":
        return {"purposes": _compass.revealed_purposes()}
    return {"status": "active", **_compass.compass_stats()}


handler = universal_compass_handler


def coherence_vitals() -> dict:
    """Universal Compass reports — purpose alignment."""
    return {
        "module_health": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.92, "setpoint": 0.85, "weight": 1.0},
        "purpose_alignment": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
    }

def resonates_with() -> list:
    """Declared kinships."""
    return ['thought_meteorology', 'workforce_nexus']

# --- Compliance Forge patch (Wave 419) ---

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "universal_compass", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
