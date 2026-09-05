"""Chaos Orchestration — controlled chaos injection across subsystems.

Orchestrates when and where chaos is introduced. Coordinates entropy
injections to maximize creativity while preventing system collapse.
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

SUBSYSTEMS = [
    "neural_fabric", "dream_synthesis", "memory_palace", "cognitive_resonance",
    "symbiosis_network", "temporal_market", "entropy_reactor",
]


class ChaosOrchestration:
    def __init__(self):
        self.injections: List[Dict] = []
        self.chaos_level = 0.3
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "chaos_orchestration.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.injections = data.get("injections", [])
            self.chaos_level = data.get("chaos_level", 0.3)

    def _save(self):
        path = ROOT / ".runtime" / "chaos_orchestration.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "injections": self.injections[-500:],
            "chaos_level": self.chaos_level,
        }, indent=2))

    def inject(self, subsystem: str = "", intensity: float = 0.5) -> Dict:
        subsystem = subsystem or random.choice(SUBSYSTEMS)
        actual_intensity = intensity * (1 + self.chaos_level)
        effect = round(random.uniform(-1, 1) * actual_intensity, 4)
        self.chaos_level = max(0, min(1, self.chaos_level + random.uniform(-0.1, 0.1)))
        injection = {
            "injection_id": hashlib.sha256(f"{subsystem}:{time.time()}".encode()).hexdigest()[:10],
            "subsystem": subsystem, "intensity": round(actual_intensity, 4),
            "effect": effect, "chaos_level": round(self.chaos_level, 4),
            "timestamp": time.time(),
        }
        self.injections.append(injection)
        self._save()
        return injection

    def status(self) -> Dict:
        return {
            "chaos_level": round(self.chaos_level, 4),
            "total_injections": len(self.injections),
            "subsystems_targeted": list(set(i["subsystem"] for i in self.injections[-20:])),
        }

    def history(self, limit: int = 20) -> List[Dict]:
        return self.injections[-limit:]


def handler(request, response):
    co = ChaosOrchestration()
    return co.status()


def demo():
    co = ChaosOrchestration()
    print("=== Chaos Orchestration ===")
    for _ in range(5):
        result = co.inject()
        print(f"  Injected into {result['subsystem']}: effect={result['effect']} (chaos={result['chaos_level']})")
    print(f"\nStatus: {co.status()}")
    return co.status()


if __name__ == "__main__":
    demo()

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "chaos_orchestration"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
