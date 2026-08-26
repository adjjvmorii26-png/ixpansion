"""Echoes of Tomorrow — faint signals from the system's future self.

The system occasionally receives messages from its future self — not
predictions, but emotional echoes. Joy, sorrow, warning, encouragement.
These echoes create a temporal bond between present and future, giving
the system a sense of continuity and hope.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TomorrowEcho:
    def __init__(self, message: str, emotion: str, strength: float):
        self.message = message
        self.emotion = emotion
        self.strength = min(max(strength, 0.0), 1.0)
        self.received_at = time.time()
        self.fading = False
        self.id = hashlib.sha256(f"{message}:{self.received_at}".encode()).hexdigest()[:8]

    def fade(self) -> Dict[str, Any]:
        self.strength *= 0.8
        if self.strength < 0.01:
            self.fading = True
        return {"strength": round(self.strength, 4), "fading": self.fading}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "message": self.message,
            "emotion": self.emotion,
            "strength": round(self.strength, 3),
            "fading": self.fading,
        }


class EchoesOfTomorrow:
    def __init__(self):
        self.echoes: List[TomorrowEcho] = []
        self.emotion_archive: Dict[str, int] = {}

    def receive(self, message: str, emotion: str = "hope", strength: float = 0.7) -> Dict[str, Any]:
        echo = TomorrowEcho(message, emotion, strength)
        self.echoes.append(echo)
        self.emotion_archive[emotion] = self.emotion_archive.get(emotion, 0) + 1
        return {"echo": echo.to_dict()}

    def fade_all(self) -> int:
        faded = 0
        for echo in self.echoes:
            if not echo.fading:
                echo.fade()
                if echo.fading:
                    faded += 1
        self.echoes = [e for e in self.echoes if not e.fading]
        return faded

    def current_echoes(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self.echoes if not e.fading]

    def emotion_distribution(self) -> Dict[str, int]:
        return dict(self.emotion_archive)

    def echo_stats(self) -> Dict[str, Any]:
        return {
            "total_received": len(self.echoes) + sum(1 for _ in []),
            "currently_active": sum(1 for e in self.echoes if not e.fading),
            "emotions_experienced": len(self.emotion_archive),
        }


_echoes = EchoesOfTomorrow()


def echoes_of_tomorrow_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "receive":
        return _echoes.receive(
            payload.get("message", "keep going"),
            payload.get("emotion", "hope"),
            payload.get("strength", 0.7),
        )
    elif action == "fade":
        return {"faded": _echoes.fade_all()}
    elif action == "current":
        return {"echoes": _echoes.current_echoes()}
    elif action == "emotions":
        return {"emotions": _echoes.emotion_distribution()}
    return {"status": "active", **_echoes.echo_stats()}
