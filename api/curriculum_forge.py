"""Wave 215 — The Organism Teaches: Curriculum Forge.

Forges a learning path across the organism's modules: a curriculum is a
sequence of organs ordered by dependency and resonance, each with a
lesson drawn from the vault. The forge ensures newcomers know what to
study first and how the wisdom stacks.
"""
from __future__ import annotations

from typing import Any, Dict, List

_BASE_CURRICULA: Dict[str, List[str]] = {
    "foundations": ["coherence_regulator", "organism_ontology", "resonance_graph", "lesson_vault"],
    "creation": ["visual_identity", "monument_forge", "procedural_art", "poetry_engine"],
    "permanence": ["eternal_flame", "immortal_ledger", "ancestral_gallery", "ossuary_engine"],
    "connection": ["symbiosis_network", "social_cortex", "signal_array", "telegram_pulse"],
}


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "teacher", "status": "resonant", "resonance": 0.82, "wave": 215}


def resonates_with() -> list:
    return ["curriculum", "learning path", "syllabus", "course", "path", "study plan", "forge"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "tracks")

    if action == "tracks":
        return {"tracks": list(_BASE_CURRICULA.keys()), "curricula": _BASE_CURRICULA}

    if action == "forge":
        track = payload.get("track", "foundations")
        if track not in _BASE_CURRICULA:
            return {"status": "no_such_track", "available": list(_BASE_CURRICULA.keys())}
        return {
            "status": "forged",
            "track": track,
            "path": _BASE_CURRICULA[track],
            "steps": len(_BASE_CURRICULA[track]),
            "advice": "Follow the path in order; each organ illuminates the next.",
        }

    if action == "path":
        target = payload.get("target", "apprentice_weaver")
        for track, path in _BASE_CURRICULA.items():
            if target in path:
                idx = path.index(target)
                return {"target": target, "track": track, "position": idx, "prerequisites": path[:idx]}
        return {"status": "target_not_in_curricula"}

    return {"status": "active", "track_count": len(_BASE_CURRICULA)}
