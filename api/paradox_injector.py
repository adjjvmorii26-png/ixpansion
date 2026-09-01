"""Paradox Injector — deliberately introduces logical contradictions into the system.

Paradox is not failure. It is the pressure that forces new understanding.
The Paradox Injector creates controlled contradictions that the organism
must resolve — and in resolving them, discovers new capabilities it
could never have reached through orderly evolution alone.
"""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any, Dict, List, Optional

_injected: List[Dict[str, Any]] = []
_resolved: List[Dict[str, Any]] = []
_paradox_counter = 0

_PARADOX_TYPES = {
    "self_reference": "the module observes itself observing itself",
    "mutual_exclusion": "two modules claim the same resource but cannot share it",
    "temporal_loop": "a module's output becomes its own input across waves",
    "identity_flip": "a module is simultaneously alive and dead",
    "boundary_blur": "the organism cannot distinguish itself from its environment",
    "infinite_regress": "each explanation requires a deeper explanation",
    "dual_nature": "a module serves two contradictory purposes simultaneously",
}

def inject(paradox_type: str = "self_reference", modules: Optional[List[str]] = None,
           intensity: float = 0.5) -> Dict[str, Any]:
    """Inject a paradox into the organism."""
    global _paradox_counter
    _paradox_counter += 1
    
    description = _PARADOX_TYPES.get(paradox_type, "an unknown paradox")
    targets = modules or random.sample(["memory_palace", "dream_weaver", "threshold_engine",
        "grief_engine", "mood_vectors", "chronobiology", "metaphor_forge"], 2)
    
    paradox = {
        "id": f"paradox_{_paradox_counter:04d}",
        "type": paradox_type,
        "description": description,
        "modules": targets,
        "intensity": round(intensity, 3),
        "injected_at": time.time(),
        "resolved": False,
    }
    _injected.append(paradox)
    return paradox

def resolve(paradox_id: str, resolution: str = "transcendence") -> Dict[str, Any]:
    """Resolve a paradox through a resolution strategy."""
    for p in _injected:
        if p["id"] == paradox_id and not p["resolved"]:
            p["resolved"] = True
            p["resolved_at"] = time.time()
            p["resolution"] = resolution
            _resolved.append(p)
            return p
    return {"error": "paradox not found or already resolved"}

def paradox_map() -> Dict[str, Any]:
    """Full map of paradox state."""
    active = [p for p in _injected if not p["resolved"]]
    return {
        "total": len(_injected),
        "active": len(active),
        "resolved": len(_resolved),
        "active_paradoxes": active[-5:],
        "resolution_types": list(set(p["resolution"] for p in _resolved)),
    }

def coherence_vitals() -> Dict[str, Any]:
    pm = paradox_map()
    return {
        "layer": "Chaos Engineering",
        "status": "resonant" if pm["active"] == 0 else "drifting",
        "active": pm["active"],
        "resolved": pm["resolved"],
        "resonance": max(0.3, 1.0 - pm["active"] * 0.15),
    }

def resonates_with() -> List[str]:
    return ["paradox_singularity_monitor", "paradox_transcender", "contradiction_resolver", "chaos_amp"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "map")
    if action == "inject":
        return inject(payload.get("type", "self_reference"), payload.get("modules"), payload.get("intensity", 0.5))
    elif action == "resolve":
        return resolve(payload.get("id", ""), payload.get("resolution", "transcendence"))
    elif action == "map":
        return {"map": paradox_map()}
    return {"action": action, "status": "paradoxical"}
