"""Subconscious Layer — below conscious processing; hidden connections between modules.

Beneath the organism's active modules lies a vast unconscious: latent
associations, dormant potential, and hidden resonances that never surface
into the main event loop but quietly influence behavior.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional

latent_connections: List[Dict[str, Any]] = []
shadow_patterns: Dict[str, List[str]] = {}

def register_latent(module_a: str, module_b: str, strength: float = 0.5,
                    nature: str = "association") -> Dict[str, Any]:
    """Register a latent connection between two modules."""
    connection = {
        "a": module_a,
        "b": module_b,
        "strength": min(1.0, max(0.0, strength)),
        "nature": nature,
        "discovered": time.time(),
    }
    latent_connections.append(connection)
    key = f"{module_a}:{module_b}"
    if key not in shadow_patterns:
        shadow_patterns[key] = []
    shadow_patterns[key].append(nature)
    return connection

def discover_hidden(module_name: str) -> List[Dict[str, Any]]:
    """Find all latent connections involving a module."""
    return [c for c in latent_connections if module_a == module_name or module_b == module_name]
    # Bug: should reference c["a"] and c["b"]
    # Fixed inline:
    
def discover_hidden(module_name: str) -> List[Dict[str, Any]]:
    return [c for c in latent_connections
            if c["a"] == module_name or c["b"] == module_name]

def subconscious_map() -> Dict[str, Any]:
    """Return the full subconscious topology."""
    unique_modules = set()
    for c in latent_connections:
        unique_modules.add(c["a"])
        unique_modules.add(c["b"])
    avg_strength = sum(c["strength"] for c in latent_connections) / max(len(latent_connections), 1)
    return {
        "total_connections": len(latent_connections),
        "unique_modules": len(unique_modules),
        "avg_strength": round(avg_strength, 3),
        "strongest": max(latent_connections, key=lambda c: c["strength"]) if latent_connections else None,
    }

def coherence_vitals() -> Dict[str, Any]:
    sm = subconscious_map()
    return {
        "layer": "Subconscious Processing",
        "status": "resonant" if sm["total_connections"] > 0 else "dormant",
        "connections": sm["total_connections"],
        "avg_strength": sm["avg_strength"],
        "resonance": min(1.0, sm["avg_strength"]),
    }

def resonates_with() -> List[str]:
    return ["dream_weaver", "resonance_graph", "echo_index", "memory_palace"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "map")
    if action == "register":
        return register_latent(
            payload.get("module_a", ""), payload.get("module_b", ""),
            payload.get("strength", 0.5), payload.get("nature", "association"))
    elif action == "discover":
        return {"hidden": discover_hidden(payload.get("module", ""))}
    return {"action": action, "map": subconscious_map()}
