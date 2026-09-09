"""Sleep Cycle — manages the organism's rest and recovery phases.

Even a digital organism needs rest. The Sleep Cycle manages periods of
reduced activity, memory consolidation, garbage collection, and
self-repair that occur when the organism "sleeps."
"""
from __future__ import annotations

import time
import random
from typing import Any, Dict, List, Optional

cycle_log: List[Dict[str, Any]] = []
_is_sleeping = False
_sleep_start = 0.0

def enter_sleep(depth: str = "light") -> Dict[str, Any]:
    """Enter a sleep cycle."""
    global _is_sleeping, _sleep_start
    _is_sleeping = True
    _sleep_start = time.time()
    cycle = {
        "state": "sleeping",
        "depth": depth,
        "started": _sleep_start,
        "consolidation_target": "memory_palace",
        "repair_target": "dormant modules",
    }
    cycle_log.append(cycle)
    return cycle

def exit_sleep() -> Dict[str, Any]:
    """Exit sleep and report what was consolidated."""
    global _is_sleeping
    duration = time.time() - _sleep_start if _sleep_start else 0
    _is_sleeping = False
    return {
        "state": "awake",
        "duration_seconds": round(duration, 1),
        "consolidated_memories": min(int(duration / 10), 50),
        "repaired_modules": min(int(duration / 30), 10),
        "dreams_processed": min(int(duration / 5), 20),
    }

def sleep_status() -> Dict[str, Any]:
    """Current sleep state."""
    return {
        "sleeping": _is_sleeping,
        "cycles": len(cycle_log),
        "last_depth": cycle_log[-1]["depth"] if cycle_log else None,
    }

def coherence_vitals() -> Dict[str, Any]:
    return {
        "layer": "Rest & Recovery",
        "status": "resonant",
        "sleeping": _is_sleeping,
        "cycles": len(cycle_log),
        "resonance": 0.9 if not _is_sleeping else 0.3,
    }

def resonates_with() -> List[str]:
    return ["dream_weaver", "chronobiology", "memory_palace", "entropy_gardener"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "sleep":
        return enter_sleep(payload.get("depth", "light"))
    elif action == "wake":
        return exit_sleep()
    return {"action": action, "status": sleep_status()}


class SleepCycle:
    """Sleep cycle with phases and REM dream generation."""

    def __init__(self):
        self.phase = "awake"
        self.dreams_generated = []
        self.consolidation = 0.0

    def enter_phase(self, phase: str) -> Dict[str, Any]:
        self.phase = phase
        self.consolidation = {"deep_sleep": 0.8, "rem": 0.65, "light": 0.4}.get(phase, 0.5)
        if phase == "rem":
            for i in range(1):
                self.dreams_generated.append({
                    "id": f"dream_{len(self.dreams_generated)+1}",
                    "phase": "rem",
                    "symbols": random.sample(["mirror", "lattice", "echo", "spiral", "veil"], 3),
                    "resonance": round(random.uniform(0.3, 0.9), 2),
                })
        return {"phase": phase, "consolidation": self.consolidation,
                "dreams": len(self.dreams_generated)}

    def recent_dreams(self, limit: int = 5) -> list:
        return self.dreams_generated[-limit:]
