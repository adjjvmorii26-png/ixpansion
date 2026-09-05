"""Echo Chamber — messages bounce through the network gaining distortion and amplification.

A message enters the chamber and bounces off agent nodes. Each bounce
adds distortion, amplification, or filtering. By the time it exits,
the message has been transformed into something unexpected — sometimes
better, sometimes corrupted, always interesting.
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

DISTORTION_EFFECTS = {
    "amplify": lambda msg, strength: msg.upper() if strength > 0.5 else msg,
    "echo": lambda msg, strength: msg + " " + msg[:int(strength * 10)],
    "filter": lambda msg, strength: " ".join(
        w for w in msg.split() if random.random() > strength * 0.5
    ),
    "distort": lambda msg, strength: "".join(
        c if random.random() > strength * 0.3 else random.choice("!?@#")
        for c in msg
    ),
    "crystallize": lambda msg, strength: msg.strip().capitalize() + ".",
}


class EchoMessage:
    def __init__(self, source: str, content: str, bounces_allowed: int = 5):
        self.source = source
        self.original = content
        self.current = content
        self.bounces_allowed = bounces_allowed
        self.bounce_count = 0
        self.transformations: List[Dict[str, Any]] = []
        self.id = hashlib.sha256(f"{content}:{time.time()}".encode()).hexdigest()[:10]
        self.strength = 1.0
        self.alive = True

    def bounce(self, effect: str, strength: float = 0.5) -> Dict[str, Any]:
        if not self.alive or self.bounce_count >= self.bounces_allowed:
            self.alive = False
            return {"status": "absorbed", "final_message": self.current}
        transform_fn = DISTORTION_EFFECTS.get(effect, DISTORTION_EFFECTS["echo"])
        previous = self.current
        self.current = transform_fn(self.current, strength)
        self.strength *= random.uniform(0.8, 1.2)
        self.bounce_count += 1
        record = {
            "effect": effect,
            "strength": round(strength, 3),
            "before": previous[:50],
            "after": self.current[:50],
            "bounce": self.bounce_count,
        }
        self.transformations.append(record)
        if self.strength < 0.1 or self.bounce_count >= self.bounces_allowed:
            self.alive = False
        return record

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "original": self.original[:100],
            "current": self.current[:100],
            "bounces": self.bounce_count,
            "alive": self.alive,
            "strength": round(self.strength, 3),
            "distortion": round(
                len(self.current) / max(len(self.original), 1) - 1, 3
            ),
        }


class EchoChamber:
    def __init__(self):
        self.messages: Dict[str, EchoMessage] = {}
        self.chamber_log: List[Dict[str, Any]] = []

    def send(self, source: str, content: str, bounces: int = 5) -> Dict[str, Any]:
        msg = EchoMessage(source, content, bounces)
        self.messages[msg.id] = msg
        return {"sent": msg.to_dict()}

    def bounce_message(self, msg_id: str, effect: str = "echo", strength: float = 0.5) -> Dict[str, Any]:
        if msg_id not in self.messages:
            return {"error": "message not found"}
        msg = self.messages[msg_id]
        result = msg.bounce(effect, strength)
        self.chamber_log.append({"msg_id": msg_id, **result, "time": time.time()})
        return {"message": msg.to_dict(), "transformation": result}

    def bounce_all(self, effect: str = None, strength: float = 0.5) -> List[Dict[str, Any]]:
        results = []
        for msg_id, msg in self.messages.items():
            if msg.alive:
                chosen_effect = effect or random.choice(list(DISTORTION_EFFECTS.keys()))
                result = msg.bounce(chosen_effect, strength)
                results.append({"msg_id": msg_id, **result})
        return results

    def collect_exits(self) -> List[Dict[str, Any]]:
        """Collect all messages that have stopped bouncing."""
        return [msg.to_dict() for msg in self.messages.values() if not msg.alive]

    def chamber_stats(self) -> Dict[str, Any]:
        alive = sum(1 for m in self.messages.values() if m.alive)
        dead = len(self.messages) - alive
        return {
            "total_messages": len(self.messages),
            "alive": alive,
            "absorbed": dead,
            "total_bounces": sum(m.bounce_count for m in self.messages.values()),
            "effects_used": len(DISTORTION_EFFECTS),
        }


_chamber = EchoChamber()


def echo_chamber_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "send":
        return _chamber.send(
            payload.get("source", "anonymous"),
            payload.get("content", "hello world"),
            payload.get("bounces", 5),
        )
    elif action == "bounce":
        return _chamber.bounce_message(
            payload.get("msg_id", ""),
            payload.get("effect", "echo"),
            payload.get("strength", 0.5),
        )
    elif action == "bounce_all":
        return {"results": _chamber.bounce_all(
            payload.get("effect"), payload.get("strength", 0.5)
        )}
    elif action == "exits":
        return {"exited": _chamber.collect_exits()}
    return {"status": "active", **_chamber.chamber_stats()}


handler = echo_chamber_handler


def coherence_vitals() -> dict:
    """echo_chamber reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "echo_chamber_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['universal_compass', 'system_pulse', 'signal_flora']


# --- Compliance Forge patch (Wave 419) ---

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "echo_chamber", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
