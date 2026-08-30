"""Resonance Memory — memories that vibrate at specific frequencies.

Memories aren't static records — they vibrate. Each memory has a
resonance frequency that determines when it activates, which other
memories it connects to, and how vividly it returns. The system
develops a harmonic memory landscape where related memories sing together.
"""
from __future__ import annotations

import hashlib
import math
import random
import time
import sys
from pathlib import Path
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class VibratingMemory:
    def __init__(self, content: str, frequency: float, agent_id: str):
        self.content = content
        self.frequency = frequency
        self.agent_id = agent_id
        self.amplitude = 1.0
        self.phase = random.uniform(0, 2 * math.pi)
        self.age = 0
        self.recalled_count = 0
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{content}:{self.timestamp}".encode()).hexdigest()[:8]

    def resonate_at(self, t: float) -> float:
        return self.amplitude * math.sin(self.frequency * t + self.phase)

    def recall(self) -> Dict[str, Any]:
        self.recalled_count += 1
        self.amplitude = min(2.0, self.amplitude * 1.1)
        return {
            "content": self.content,
            "frequency": round(self.frequency, 3),
            "amplitude": round(self.amplitude, 3),
            "recall_count": self.recalled_count,
        }

    def decay(self):
        self.amplitude *= 0.95
        self.age += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content[:60],
            "frequency": round(self.frequency, 3),
            "amplitude": round(self.amplitude, 3),
            "agent_id": self.agent_id,
            "recalled": self.recalled_count,
            "age": self.age,
        }


class ResonanceMemory:
    def __init__(self):
        self.memories: List[VibratingMemory] = []
        self.harmonic_groups: List[List[str]] = []

    def store(self, content: str, frequency: float = None, agent_id: str = "rememberer") -> Dict[str, Any]:
        freq = frequency or random.uniform(0.1, 10.0)
        memory = VibratingMemory(content, freq, agent_id)
        self.memories.append(memory)
        return {"stored": memory.to_dict()}

    def recall_by_frequency(self, target_freq: float, tolerance: float = 1.0) -> List[Dict[str, Any]]:
        recalled = []
        for mem in self.memories:
            if abs(mem.frequency - target_freq) <= tolerance:
                recalled.append(mem.recall())
        recalled.sort(key=lambda x: x["amplitude"], reverse=True)
        return recalled

    def find_harmonics(self) -> List[Dict[str, Any]]:
        groups: Dict[str, List[str]] = {}
        for mem in self.memories:
            bucket = round(mem.frequency) 
            groups.setdefault(str(bucket), []).append(mem.id)
        harmonics = [{"frequency_band": k, "memories": v} for k, v in groups.items() if len(v) > 1]
        self.harmonic_groups = [[mid for mid in g["memories"]] for g in harmonics]
        return harmonics

    def tick(self):
        for mem in self.memories:
            mem.decay()

    def memory_stats(self) -> Dict[str, Any]:
        total_amplitude = sum(m.amplitude for m in self.memories)
        return {
            "total_memories": len(self.memories),
            "total_amplitude": round(total_amplitude, 3),
            "avg_frequency": round(
                sum(m.frequency for m in self.memories) / max(len(self.memories), 1), 3
            ),
            "harmonic_groups": len(self.harmonic_groups),
            "total_recalls": sum(m.recalled_count for m in self.memories),
        }


_resonance = ResonanceMemory()


def resonance_memory_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "store":
        return _resonance.store(
            payload.get("content", "a vibrating memory"),
            payload.get("frequency"),
            payload.get("agent_id", "rememberer"),
        )
    elif action == "recall":
        return {"recalled": _resonance.recall_by_frequency(
            payload.get("frequency", 5.0),
            payload.get("tolerance", 1.0),
        )}
    elif action == "harmonics":
        return {"harmonics": _resonance.find_harmonics()}
    elif action == "tick":
        _resonance.tick()
        return {"status": "decayed"}
    return {"status": "active", **_resonance.memory_stats()}


handler = resonance_memory_handler


def coherence_vitals() -> dict:
    """resonance_memory reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance_memory_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['memory_crystals', 'system_pulse', 'pattern_sprout']

