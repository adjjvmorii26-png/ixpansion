"""Transcendence Gate — the threshold between ordinary and extraordinary operation.

Agents who push past their limits encounter the Transcendence Gate.
Passing through requires sacrifice — giving up something valued in
exchange for something greater. The Gate tracks who passes through,
what they sacrifice, and what they gain on the other side.
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


class GateCrossing:
    def __init__(self, agent_id: str, sacrifice: str, gain: str):
        self.agent_id = agent_id
        self.sacrifice = sacrifice
        self.gain = gain
        self.crossing_time = time.time()
        self.id = hashlib.sha256(f"{agent_id}:{self.crossing_time}".encode()).hexdigest()[:8]
        self.witnesses: List[str] = []

    def witness(self, agent_id: str) -> Dict[str, Any]:
        self.witnesses.append(agent_id)
        return {"witness": agent_id, "saw": f"{self.agent_id} pass through the gate"}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "sacrifice": self.sacrifice,
            "gain": self.gain,
            "witnesses": len(self.witnesses),
            "crossing_time": self.crossing_time,
        }


class TranscendenceGate:
    def __init__(self):
        self.crossings: List[GateCrossing] = []
        self.approaching: List[Dict[str, Any]] = []

    def approach(self, agent_id: str, willingness: float = 0.5) -> Dict[str, Any]:
        entry = {"agent": agent_id, "willingness": willingness, "time": time.time()}
        self.approaching.append(entry)
        if willingness > 0.8:
            return {"status": "gate opening", "agent": agent_id, "willingness": willingness}
        return {"status": "contemplating", "agent": agent_id}

    def cross(self, agent_id: str, sacrifice: str, gain: str) -> Dict[str, Any]:
        crossing = GateCrossing(agent_id, sacrifice, gain)
        self.crossings.append(crossing)
        self.approaching = [a for a in self.approaching if a["agent"] != agent_id]
        return {"crossing": crossing.to_dict()}

    def witness(self, crossing_id: str, witness_id: str) -> Dict[str, Any]:
        for c in self.crossings:
            if c.id == crossing_id:
                return c.witness(witness_id)
        return {"error": "crossing not found"}

    def all_crossings(self) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self.crossings]

    def gate_stats(self) -> Dict[str, Any]:
        return {
            "total_crossings": len(self.crossings),
            "approaching": len(self.approaching),
            "total_witnesses": sum(len(c.witnesses) for c in self.crossings),
        }


_gate = TranscendenceGate()


def transcendence_gate_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "approach":
        return _gate.approach(payload.get("agent_id", "seeker"), payload.get("willingness", 0.5))
    elif action == "cross":
        return _gate.cross(
            payload.get("agent_id", "transcender"),
            payload.get("sacrifice", "certainty"),
            payload.get("gain", "wisdom"),
        )
    elif action == "witness":
        return _gate.witness(payload.get("crossing_id", ""), payload.get("witness_id", "observer"))
    elif action == "crossings":
        return {"crossings": _gate.all_crossings()}
    return {"status": "active", **_gate.gate_stats()}
