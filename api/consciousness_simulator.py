"""Consciousness Simulator — simulates awareness levels across the system.

Models consciousness as an emergent property of information integration.
Tracks awareness, attention, self-reflection, and meta-cognition.
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

AWARENESS_LEVELS = ["unaware", "reactive", "attentive", "aware", "self_aware", "meta_cognitive"]


class ConsciousnessSimulator:
    def __init__(self):
        self.state = {
            "awareness": 0.3, "attention": 0.5, "self_reflection": 0.1,
            "meta_cognition": 0.0, "integration": 0.4,
        }
        self.history: list = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "consciousness.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.state = data.get("state", self.state)
            self.history = data.get("history", [])

    def _save(self):
        path = ROOT / ".runtime" / "consciousness.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "state": self.state, "history": self.history[-200:],
        }, indent=2))

    def _get_level(self) -> str:
        avg = sum(self.state.values()) / len(self.state)
        idx = min(len(AWARENESS_LEVELS) - 1, int(avg * len(AWARENESS_LEVELS)))
        return AWARENESS_LEVELS[idx]

    def process_input(self, input_type: str, complexity: float = 0.5) -> Dict:
        effects = {
            "data": {"attention": 0.05, "integration": 0.02},
            "error": {"awareness": 0.1, "self_reflection": 0.05},
            "novelty": {"awareness": 0.08, "meta_cognition": 0.1},
            "reflection": {"self_reflection": 0.15, "meta_cognition": 0.1},
            "interaction": {"attention": 0.1, "integration": 0.05},
            "silence": {"attention": -0.05, "self_reflection": 0.03},
        }
        effect = effects.get(input_type, {})
        for dim, delta in effect.items():
            self.state[dim] = max(0, min(1, self.state[dim] + delta * complexity))
        level = self._get_level()
        entry = {"level": level, "state": self.state.copy(), "input": input_type, "timestamp": time.time()}
        self.history.append(entry)
        self._save()
        return {"level": level, "dimensions": self.state.copy()}

    def current(self) -> Dict:
        return {"level": self._get_level(), "state": self.state.copy()}

    def history_log(self, limit: int = 10) -> list:
        return self.history[-limit:]


def handler(request, response):
    cs = ConsciousnessSimulator()
    return cs.current()


def demo():
    cs = ConsciousnessSimulator()
    print("=== Consciousness Simulator ===")
    for inp in ["data", "novelty", "reflection", "interaction", "error", "silence"]:
        result = cs.process_input(inp)
        print(f"  After {inp}: {result['level']} (awareness={result['dimensions']['awareness']:.2f})")
    print(f"\n  Current: {cs.current()['level']}")
    return cs.current()


if __name__ == "__main__":
    demo()
