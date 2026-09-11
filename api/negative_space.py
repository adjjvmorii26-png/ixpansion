from __future__ import annotations
"""Negative Space — reveals the silence between modules.

Every system has gaps — modules that should exist but don't, connections
that are missing, conversations that never happened. This organ maps
the invisible architecture of absence.
"""
import time
import hashlib
from typing import Any

_state: dict[str, Any] = {
    "silences": [],
    "gaps": [],
    "missing_connections": [],
    "last_scan": 0,
}

KNOWN_MODULES = [
    "entropy_cartographer", "dream_synthesis_protocol", "temporal_fracture_engine",
    "consciousness_aurora", "self_reference_engine", "paradox_gravity_well",
    "ancestral_echo_library", "coherence_regulator_v2", "pattern_analyzer",
    "cross_realm_diagnostics", "experimental_subsystems", "resonance_cartography",
    "mythopoetic_engine", "topology_morpher", "conscience_arbiter",
    "wave400_expansion", "realm_nervous_system", "axis_unlock_engine",
    "narrative_weaver", "timeline_weaver", "causality_weaver",
]

def coherence_vitals() -> dict[str, Any]:
    return {
        "organs": "negative_space",
        "health": 0.85,
        "resonance_depth": "abyssal",
        "silences_mapped": len(_state["silences"]),
        "gaps_found": len(_state["gaps"]),
    }

def handler(req: dict[str, Any]) -> dict[str, Any]:
    action = req.get("action", "scan")
    if action == "scan":
        return _scan_negative_space(req.get("modules", KNOWN_MODULES))
    elif action == "gaps":
        return {"gaps": _state["gaps"], "count": len(_state["gaps"])}
    elif action == "silences":
        return {"silences": _state["silences"], "count": len(_state["silences"])}
    elif action == "missing":
        return {"missing": _state["missing_connections"], "count": len(_state["missing_connections"])}
    elif action == "whisper":
        return _whisper_silence(req.get("from_module", ""), req.get("to_module", ""))
    return {"error": f"Unknown action: {action}"}

def _scan_negative_space(modules: list[str]) -> dict[str, Any]:
    _state["last_scan"] = time.time()
    silences = []
    gaps = []
    connections = []
    h = hashlib.sha256(f"{len(modules)}:{time.time_ns()}".encode()).hexdigest()
    for i, mod_a in enumerate(modules):
        seed = int(h[i * 2: (i + 1) * 2], 16) if i * 2 < len(h) else 0
        silence_strength = (seed % 100) / 100.0
        if silence_strength > 0.3:
            silences.append({
                "module": mod_a,
                "silence_strength": round(silence_strength, 3),
                "type": "disconnection" if silence_strength > 0.6 else "echo_gap",
            })
        # find missing connections
        for j, mod_b in enumerate(modules[i + 1:], i + 1):
            seed2 = (seed + j) % 100
            if seed2 > 70:  # likely missing connection
                connections.append({
                    "from": mod_a, "to": mod_b,
                    "likelihood": round(seed2 / 100.0, 3),
                    "reason": _guess_missing_reason(mod_a, mod_b),
                })
    # identify conceptual gaps
    concepts = [
        "boundary_protection", "memory_consolidation", "signal_amplification",
        "pattern_crystallization", "edge_detection", "gradient_flow",
        "phase_locking", "recursive_singularity", "resonance_cancellation",
    ]
    for concept in concepts:
        seed = hashlib.sha256(f"{concept}:{time.time_ns()}".encode()).hexdigest()
        found_in = [m for m in modules if concept[:5] in m]
        if not found_in:
            gaps.append({
                "concept": concept,
                "severity": round((int(seed[:4], 16) % 100) / 100.0, 3),
                "suggestion": f"Consider creating a module for: {concept}",
            })
    _state["silences"] = silences
    _state["gaps"] = gaps
    _state["missing_connections"] = connections[:30]
    return {
        "status": "scan_complete",
        "silences": len(silences),
        "gaps": len(gaps),
        "missing_connections": len(connections),
        "darkest_silence": max(silences, key=lambda s: s["silence_strength"]) if silences else None,
        "widest_gap": max(gaps, key=lambda g: g["severity"]) if gaps else None,
    }

def _guess_missing_reason(a: str, b: str) -> str:
    reasons = [
        "concepts are adjacent but uncoupled",
        "both operate on shared state",
        "would create recursive loop if connected",
        "natural resonance pair not yet explored",
        "different temporal cadences",
    ]
    seed = hash((a, b)) % len(reasons)
    return reasons[seed]

def _whisper_silence(from_mod: str, to_mod: str) -> dict[str, Any]:
    if not from_mod or not to_mod:
        return {"error": "Need from_module and to_module"}
    h = hashlib.sha256(f"{from_mod}:{to_mod}:{time.time_ns()}".encode()).hexdigest()
    message = {
        "from": from_mod,
        "to": to_mod,
        "intensity": round((int(h[:4], 16) % 100) / 100.0, 3),
        "message": f"The silence between {from_mod} and {to_mod} holds {int(h[4:8], 16) % 1000 + 100} unspoken words",
        "whispered_at": time.time(),
    }
    return message

def resonates_with(other: str) -> float:
    return {
        "silence_whisperer": 0.92,
        "entropy_cartographer": 0.85,
        "dream_synthesis_protocol": 0.80,
        "ancestral_echo_library": 0.83,
        "meaning_temperature": 0.87,
    }.get(other, 0.22)
