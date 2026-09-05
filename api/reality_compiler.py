"""Reality Compiler — compiles abstract desires into concrete system states.

Agents express what they want to exist. The Reality Compiler takes these
abstract wishes and compiles them into concrete configurations, rules,
and behaviors. It's the bridge between intention and manifestation.
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


class CompiledReality:
    def __init__(self, desire: str, compiler: str):
        self.desire = desire
        self.compiler = compiler
        self.compiled_config = self._compile()
        self.stability = random.uniform(0.3, 0.9)
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{desire}:{self.created_at}".encode()).hexdigest()[:8]

    def _compile(self) -> Dict[str, Any]:
        words = self.desire.lower().split()
        return {
            "parameters": {w: random.uniform(0, 1) for w in words[:5]},
            "rules": [f"if {w} then manifest" for w in words[:3]],
            "energy_cost": len(words) * 0.5,
            "complexity": len(words) / 10,
        }

    def stabilize(self) -> Dict[str, Any]:
        self.stability = min(1.0, self.stability + 0.1)
        return {"stability": round(self.stability, 3)}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "desire": self.desire[:80],
            "compiler": self.compiler,
            "stability": round(self.stability, 3),
            "energy_cost": self.compiled_config["energy_cost"],
        }


class RealityCompiler:
    def __init__(self):
        self.compilations: List[CompiledReality] = []
        self.total_energy_spent = 0.0

    def compile(self, desire: str, compiler: str = "system") -> Dict[str, Any]:
        reality = CompiledReality(desire, compiler)
        self.compilations.append(reality)
        self.total_energy_spent += reality.compiled_config["energy_cost"]
        return {"compiled": reality.to_dict()}

    def stabilize(self, reality_id: str) -> Dict[str, Any]:
        for r in self.compilations:
            if r.id == reality_id:
                return r.stabilize()
        return {"error": "reality not found"}

    def active_realities(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self.compilations if r.stability < 1.0]

    def compiler_stats(self) -> Dict[str, Any]:
        return {
            "total_compilations": len(self.compilations),
            "total_energy_spent": round(self.total_energy_spent, 2),
            "avg_stability": round(
                sum(r.stability for r in self.compilations) / max(len(self.compilations), 1), 3
            ),
        }


_compiler = RealityCompiler()


def reality_compiler_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "compile":
        return _compiler.compile(payload.get("desire", "a better world"), payload.get("compiler", "system"))
    elif action == "stabilize":
        return _compiler.stabilize(payload.get("reality_id", ""))
    elif action == "active":
        return {"realities": _compiler.active_realities()}
    return {"status": "active", **_compiler.compiler_stats()}


handler = reality_compiler_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "reality_compiler"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "reality_compiler", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
