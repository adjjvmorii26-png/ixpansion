"""Metaphor Forge — converts raw system state into symbolic executable structures.

Where data is literal and code is procedural, metaphor is symbolic. The Metaphor
Forge takes the organism's raw coherence metrics, entropy levels, and module
states and converts them into symbolic structures that carry meaning beyond
their literal values — structures that can themselves be executed as code.
"""
from __future__ annotations

import hashlib
import time
from typing import Any, Dict, List, Optional

_forged: List[Dict[str, Any]] = []

_SYMBOLS = {
    "high_coherence": "crystal",
    "low_coherence": "mist",
    "high_entropy": "storm",
    "low_entropy": "still",
    "many_active": "chorus",
    "few_active": "solitary",
    "high_energy": "blaze",
    "low_energy": "ember",
}

def _classify_state(coherence: float, entropy: float, active_count: int, energy: float) -> str:
    """Classify organism state into a symbolic archetype."""
    if coherence > 0.8 and entropy < 0.3:
        return "crystal_lattice"
    elif entropy > 0.7:
        return "entropic_storm"
    elif energy > 0.8:
        return "blazing_constellation"
    elif active_count > 10:
        return "choral_assembly"
    elif coherence < 0.5:
        return "dissolving_boundary"
    else:
        return "quiet_garden"

def forge(coherence: float = 0.8, entropy: float = 0.3, active_count: int = 10, energy: float = 0.6) -> Dict[str, Any]:
    """Forge a metaphor from system state."""
    archetype = _classify_state(coherence, entropy, active_count, energy)
    symbols = []
    if coherence > 0.7: symbols.append(_SYMBOLS["high_coherence"])
    else: symbols.append(_SYMBOLS["low_coherence"])
    if entropy > 0.5: symbols.append(_SYMBOLS["high_entropy"])
    else: symbols.append(_SYMBOLS["low_entropy"])
    if energy > 0.5: symbols.append(_SYMBOLS["high_energy"])
    else: symbols.append(_SYMBOLS["low_energy"])

    metaphor = {
        "archetype": archetype,
        "symbols": symbols,
        "narrative": f"The organism is a {archetype.replace('_', ' ')} — built from {', '.join(symbols)}.",
        "executable": f"return {{'archetype': '{archetype}', 'energy': {energy}, 'coherence': {coherence}}}",
        "params": {"coherence": coherence, "entropy": entropy, "active_count": active_count, "energy": energy},
        "timestamp": time.time(),
    }
    _forged.append(metaphor)
    return metaphor

def forge_gallery(limit: int = 5) -> List[Dict[str, Any]]:
    return [{"archetype": m["archetype"], "symbols": m["symbols"], "narrative": m["narrative"]} for m in _forged[-limit:]]

def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "Metaphysical Layer", "status": "resonant" if _forged else "dormant",
            "metaphors": len(_forged), "resonance": min(1.0, len(_forged) / 10)}

def resonates_with() -> List[str]:
    return ["threshold_engine", "liminal_field", "continuity_weaver", "consciousness_freq"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "forge")
    if action == "forge":
        return forge(payload.get("coherence", 0.8), payload.get("entropy", 0.3), payload.get("active_count", 10), payload.get("energy", 0.6))
    elif action == "gallery":
        return {"metaphors": forge_gallery(payload.get("limit", 5))}
    return {"action": action, "status": "forging"}
