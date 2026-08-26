"""Future Echo — faint traces of probable futures leak into the present.

The system occasionally receives faint echoes from probable futures —
not strong enough to be predictions, but enough to influence current
decisions. Future echoes create a subtle premonition effect that makes
the system slightly better at avoiding disasters and finding opportunities.
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


class FutureEcho:
    def __init__(self, probability: float, signal: str, source_module: str):
        self.probability = min(max(probability, 0.0), 1.0)
        self.signal = signal
        self.source_module = source_module
        self.faded = False
        self.strength = self.probability * 0.5
        self.observed_by: List[str] = []
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{signal}:{self.timestamp}".encode()).hexdigest()[:8]

    def observe(self, agent_id: str) -> Dict[str, Any]:
        self.observed_by.append(agent_id)
        self.strength *= 0.8
        if self.strength < 0.01:
            self.faded = True
        return {
            "echo_id": self.id,
            "signal": self.signal,
            "probability": round(self.probability, 3),
            "remaining_strength": round(self.strength, 4),
            "observer": agent_id,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "signal": self.signal,
            "source": self.source_module,
            "probability": round(self.probability, 3),
            "strength": round(self.strength, 4),
            "faded": self.faded,
            "observers": len(self.observed_by),
        }


class FutureEchoSystem:
    def __init__(self):
        self.echoes: List[FutureEcho] = []
        self.echo_log: List[Dict[str, Any]] = []
        self.strength_history: List[float] = []

    def receive_echo(self, signal: str, probability: float = 0.5, source: str = "quantum_field") -> Dict[str, Any]:
        echo = FutureEcho(probability, signal, source)
        self.echoes.append(echo)
        self.echo_log.append({
            "received": signal,
            "probability": probability,
            "source": source,
            "time": time.time(),
        })
        return {"echo": echo.to_dict()}

    def observe_echo(self, echo_idx: int, agent_id: str) -> Dict[str, Any]:
        active_echoes = [e for e in self.echoes if not e.faded]
        if 0 <= echo_idx < len(active_echoes):
            return active_echoes[echo_idx].observe(agent_id)
        return {"error": "echo not found or faded"}

    def current_echoes(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self.echoes if not e.faded]

    def fade_all(self) -> int:
        faded = 0
        for echo in self.echoes:
            if not echo.faded:
                echo.strength *= 0.5
                if echo.strength < 0.01:
                    echo.faded = True
                    faded += 1
        self.strength_history.append(sum(e.strength for e in self.echoes if not e.faded))
        return faded

    def prophecy_strength(self) -> Dict[str, Any]:
        active = [e for e in self.echoes if not e.faded]
        if not active:
            return {"strength": 0, "message": "no active echoes"}
        avg_prob = sum(e.probability for e in active) / len(active)
        avg_strength = sum(e.strength for e in active) / len(active)
        return {
            "active_echoes": len(active),
            "avg_probability": round(avg_prob, 3),
            "avg_strength": round(avg_strength, 4),
            "total_received": len(self.echoes),
        }


_echo_system = FutureEchoSystem()


def future_echo_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "receive":
        return _echo_system.receive_echo(
            payload.get("signal", "a disturbance"),
            payload.get("probability", 0.5),
            payload.get("source", "quantum_field"),
        )
    elif action == "observe":
        return _echo_system.observe_echo(
            payload.get("echo_idx", 0),
            payload.get("agent_id", "perceiver"),
        )
    elif action == "current":
        return {"echoes": _echo_system.current_echoes()}
    elif action == "fade":
        return {"faded": _echo_system.fade_all()}
    return {"status": "active", **_echo_system.prophecy_strength()}
