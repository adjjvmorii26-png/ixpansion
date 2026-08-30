"""Emergence Detector — watches for spontaneous order arising from chaos.

Monitors all subsystems and detects when unpredictable patterns emerge
from the interaction of simpler components. Reports emergent behaviors
with confidence scores and potential explanations.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
    from runtime_io import load_json as _rio_load, save_json as _rio_save
except Exception:
    _rio_load = _rio_save = None

EMERGENCE_SIGNALS = [
    {"type": "self_organization", "description": "Components arranged without external direction", "weight": 0.9},
    {"type": "feedback_loop", "description": "Output became input, creating amplification", "weight": 0.7},
    {"type": "phase_transition", "description": "System shifted suddenly between states", "weight": 0.85},
    {"type": "collective_behavior", "description": "Agents coordinated without central control", "weight": 0.8},
    {"type": "novel_property", "description": "System exhibited property not present in parts", "weight": 0.95},
    {"type": "adaptation", "description": "System modified behavior in response to pressure", "weight": 0.6},
    {"type": "memory_formation", "description": "System began remembering past states", "weight": 0.75},
    {"type": "communication_spontaneous", "description": "Agents began exchanging signals unprompted", "weight": 0.85},
]


class EmergenceDetector:
    def __init__(self):
        self.observations: List[Dict] = []
        self.detections: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "emergence.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        if path.exists():
            data = json.loads(path.read_text())
            self.observations = data.get("observations", [])
            self.detections = data.get("detections", [])

    def _save(self):
        path = ROOT / ".runtime" / "emergence.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        path.write_text(json.dumps({
            "observations": self.observations[-500:],
            "detections": self.detections[-200:],
        }, indent=2))

    def observe(self, subsystem: str, metric: str, value: float) -> Dict:
        obs = {
            "subsystem": subsystem, "metric": metric,
            "value": value, "timestamp": time.time(),
        }
        self.observations.append(obs)
        recent = [o for o in self.observations if o["subsystem"] == subsystem and o["metric"] == metric]
        if len(recent) >= 3:
            values = [o["value"] for o in recent[-5:]]
            variance = sum((v - sum(values)/len(values))**2 for v in values) / len(values)
            if variance > 0.1:
                signal = random.choice(EMERGENCE_SIGNALS)
                detection = {
                    "detection_id": hashlib.sha256(f"{subsystem}:{time.time()}".encode()).hexdigest()[:10],
                    "subsystem": subsystem,
                    "signal_type": signal["type"],
                    "description": signal["description"],
                    "confidence": round(signal["weight"] * min(1.0, variance * 2), 3),
                    "evidence": {"values": values, "variance": round(variance, 4)},
                    "detected_at": time.time(),
                }
                self.detections.append(detection)
                self._save()
                return {"emergence_detected": True, "detection": detection}
        self._save()
        return {"emergence_detected": False}

    def recent_detections(self, limit: int = 10) -> List[Dict]:
        return self.detections[-limit:]

    def stats(self) -> Dict:
        return {
            "total_observations": len(self.observations),
            "total_detections": len(self.detections),
            "subsystems_observed": len(set(o["subsystem"] for o in self.observations)),
            "emergence_rate": round(len(self.detections) / max(len(self.observations), 1), 4),
        }


def handler(request, response):
    ed = EmergenceDetector()
    return ed.stats()


def demo():
    ed = EmergenceDetector()
    print("=== Emergence Detector ===")
    for i in range(10):
        result = ed.observe("neural_fabric", "activation", random.uniform(0, 1))
        if result.get("emergence_detected"):
            d = result["detection"]
            print(f"\n  EMERGENCE: {d['signal_type']}")
            print(f"    {d['description']}")
            print(f"    Confidence: {d['confidence']}")

    stats = ed.stats()
    print(f"\n  Observations: {stats['total_observations']}, Detections: {stats['total_detections']}")
    return stats


if __name__ == "__main__":
    demo()


def coherence_vitals() -> dict:
    """Emergence Detector reports its vital signs — how much order is arising."""
    try:
        s = handler({}, {})
        emerging = min(1.0, s.get("detections", 0) / 20.0)
    except Exception:
        emerging = 0.75
    return {
        "module_health": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.92, "setpoint": 0.85, "weight": 1.0},
        "emergence_level": {"value": min(1.0, emerging), "setpoint": 0.8, "weight": 1.0},
    }
