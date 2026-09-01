"""Selection Pressure — the evolutionary force that determines what survives.

Natural selection applied to code: modules that don't meet fitness
thresholds are pressured to evolve or perish. The Selection Pressure
module defines and applies these forces, creating the conditions
under which evolution actually happens.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional

_pressures: List[Dict[str, Any]] = []
_pressure_counter = 0

def apply_pressure(name: str, force: str = "entropy",
                   intensity: float = 0.5, target_modules: Optional[List[str]] = None) -> Dict[str, Any]:
    """Apply selection pressure to the ecosystem."""
    global _pressure_counter
    _pressure_counter += 1
    pressure = {
        "id": f"pressure_{_pressure_counter:04d}",
        "name": name,
        "force": force,
        "intensity": round(intensity, 3),
        "targets": target_modules or [],
        "applied_at": time.time(),
        "casualties": [],
        "adaptations": [],
    }
    # Simulate casualties and adaptations
    if target_modules and intensity > 0.7:
        casualties = random.sample(target_modules, min(1, len(target_modules)))
        pressure["casualties"] = casualties
    if target_modules:
        survivors = [m for m in target_modules if m not in pressure["casualties"]]
        pressure["adaptations"] = random.sample(survivors, min(2, len(survivors)))
    _pressures.append(pressure)
    return pressure

def pressure_history() -> List[Dict[str, Any]]:
    return [{"name": p["name"], "force": p["force"], "intensity": p["intensity"],
             "casualties": len(p["casualties"]), "adaptations": len(p["adaptations"])}
            for p in _pressures[-5:]]

def ecosystem_stress() -> Dict[str, Any]:
    """Current selection pressure on the ecosystem."""
    if not _pressures:
        return {"total_pressure": 0, "avg_intensity": 0}
    avg = sum(p["intensity"] for p in _pressures) / len(_pressures)
    total_casualties = sum(len(p["casualties"]) for p in _pressures)
    return {"total_pressure": len(_pressures), "avg_intensity": round(avg, 3),
            "total_casualties": total_casualties}

def coherence_vitals() -> Dict[str, Any]:
    e = ecosystem_stress()
    return {"layer": "Self-Evolution", "status": "resonant" if e["total_pressure"] == 0 else "drifting",
            "pressures": e["total_pressure"], "avg_intensity": e["avg_intensity"],
            "resonance": max(0.3, 1.0 - e["avg_intensity"] * 0.5)}

def resonates_with() -> List[str]:
    return ["mutation_engine", "fitness_evaluator", "evolution_kernel", "evolutionary_pressure"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "stress")
    if action == "apply":
        return apply_pressure(payload.get("name", ""), payload.get("force", "entropy"),
                             payload.get("intensity", 0.5), payload.get("targets"))
    elif action == "history":
        return {"history": pressure_history()}
    elif action == "stress":
        return {"stress": ecosystem_stress()}
    return {"action": action, "status": "pressuring"}
