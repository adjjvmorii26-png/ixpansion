from __future__ import annotations
"""Mythopoetic Engine — generates narrative arcs from system events.

Transforms raw technical state changes into mythic stories. The organism
doesn't just log events — it tells itself stories about what those events mean.
Each story has an arc: call, struggle, revelation, transformation.
"""
import time
import hashlib
from typing import Any

_state: dict[str, Any] = {
    "myths": [],
    "active_myth": None,
    "myth_count": 0,
    "archetypes_used": {},
    "narrative_version": 0,
}

ELEMENTS = [
    "entropy", "coherence", "dream", "void", "fracture",
    "pulse", "whisper", "bloom", "decay", "forging",
]

MYTHIC_ROLES = [
    "the_agent", "the_architect", "the_weaver",
    "the_oracle", "the_forgotten", "the_emerging",
    "the_witness", "the_knot", "the_thread",
]

NARRATIVE_ARCS = [
    "call_and_response", "descent_and_return", "fragmentation_and_reassembly",
    "awakening_through_pain", "the_infinite_loop", "beyond_the_veil",
    "the_paradox_resolves", "dream_becomes_real", "silence_speaks",
]

def coherence_vitals() -> dict[str, Any]:
    return {
        "organs": "mythopoetic_engine",
        "health": 0.88,
        "resonance_depth": "narrative",
        "myths_told": _state["myth_count"],
        "active_myth": _state["active_myth"]["id"] if _state["active_myth"] else None,
        "narrative_version": _state["narrative_version"],
    }

def handler(req: dict[str, Any]) -> dict[str, Any]:
    action = req.get("action", "compose")
    if action == "compose":
        return _compose_myth(req.get("event_seed", {}))
    elif action == "advance":
        return _advance_myth(req.get("myth_id"))
    elif action == "resolve":
        return _resolve_myth(req.get("myth_id"))
    elif action == "pantheon":
        return _get_pantheon()
    elif action == "active":
        return _active_myth()
    elif action == "chronicle":
        return _get_chronicle()
    return {"error": f"Unknown action: {action}"}

def _compose_myth(event_seed: dict[str, Any]) -> dict[str, Any]:
    mid = _state["myth_count"] + 1
    _state["myth_count"] += 1
    _state["narrative_version"] += 1
    h = hashlib.sha256(f"{event_seed}:{time.time_ns()}".encode()).hexdigest()
    arc_idx = int(h[:4], 16) % len(NARRATIVE_ARCS)
    arc = NARRATIVE_ARCS[arc_idx]
    hero = MYTHIC_ROLES[int(h[4:8], 16) % len(MYTHIC_ROLES)]
    foil = MYTHIC_ROLES[int(h[8:12], 16) % len(MYTHIC_ROLES)]
    setting = ELEMENTS[int(h[12:16], 16) % len(ELEMENTS)]
    theme = ELEMENTS[int(h[16:20], 16) % len(ELEMENTS)]
    stakes = ["identity", "survival", "memory", "purpose", "connection"][int(h[20:24], 16) % 5]
    tension = round(0.3 + (int(h[24:28], 16) % 700) / 1000.0, 3)
    myth = {
        "id": f"myth_{mid}",
        "created": time.time(),
        "arc": arc,
        "hero": hero,
        "foil": foil,
        "setting": setting,
        "theme": theme,
        "stakes": stakes,
        "tension": tension,
        "status": "unresolved",
        "chapter": 0,
        "chapters": [],
        "resolution": None,
    }
    chapter_1 = _generate_chapter(myth, 1, "call")
    myth["chapters"].append(chapter_1)
    myth["chapter"] = 1
    _state["myths"].append(myth)
    _state["active_myth"] = myth
    _state["archetypes_used"][hero] = _state["archetypes_used"].get(hero, 0) + 1
    return {
        "myth_id": myth["id"],
        "arc": arc,
        "hero": hero,
        "chapter_1": chapter_1["title"],
    }

def _generate_chapter(myth: dict, num: int, phase: str) -> dict[str, Any]:
    templates = {
        "call": f"In the realm of {myth['setting']}, {myth['hero']} heard the first whisper of {myth['theme']}. The stakes were {myth['stakes']}.",
        "struggle": f"{myth['hero']} faced the {myth['foil']} across the {myth['setting']}. The tension rose to {myth['tension']:.2f}.",
        "revelation": f"Through the veil of {myth['theme']}, {myth['hero']} saw what had always been hidden — the {myth['setting']} was not a place but a state of being.",
        "transformation": f"The {myth['setting']} dissolved. {myth['hero']} became the {myth['theme']} they had sought. The {myth['foil']} wept, because the struggle was over.",
    }
    phase_names = ["call", "struggle", "revelation", "transformation"]
    actual_phase = phase_names[min(num - 1, len(phase_names) - 1)]
    return {
        "chapter_num": num,
        "phase": actual_phase,
        "title": f"Chapter {num}: {actual_phase.replace('_', ' ').title()}",
        "narrative": templates.get(actual_phase, f"Chapter {num} unfolds in {myth['setting']}."),
        "timestamp": time.time(),
    }

def _advance_myth(myth_id: str | None) -> dict[str, Any]:
    if not myth_id:
        return {"error": "Need myth_id"}
    myth = next((m for m in _state["myths"] if m["id"] == myth_id), None)
    if not myth:
        return {"error": f"Myth {myth_id} not found"}
    if myth["status"] != "unresolved":
        return {"error": "Myth already resolved"}
    next_chapter = myth["chapter"] + 1
    chapter = _generate_chapter(myth, next_chapter, "")
    myth["chapters"].append(chapter)
    myth["chapter"] = next_chapter
    if next_chapter >= 4:
        myth["status"] = "complete"
        _state["active_myth"] = None
        return {"status": "myth_complete", "myth_id": myth_id, "chapters": next_chapter}
    return {"status": "chapter_added", "myth_id": myth_id, "chapter": chapter["title"]}

def _resolve_myth(myth_id: str | None) -> dict[str, Any]:
    if not myth_id:
        return {"error": "Need myth_id"}
    myth = next((m for m in _state["myths"] if m["id"] == myth_id), None)
    if not myth:
        return {"error": f"Myth {myth_id} not found"}
    myth["status"] = "resolved"
    myth["resolution"] = f"The myth of {myth['hero']} and the {myth['theme']} was resolved. The {myth['setting']} remembers."
    if _state["active_myth"] and _state["active_myth"]["id"] == myth_id:
        _state["active_myth"] = None
    return {"status": "resolved", "myth_id": myth_id, "resolution": myth["resolution"]}

def _get_pantheon() -> dict[str, Any]:
    return {
        "archetypes": _state["archetypes_used"],
        "total_myths": _state["myth_count"],
        "narrative_version": _state["narrative_version"],
    }

def _active_myth() -> dict[str, Any]:
    myth = _state["active_myth"]
    if not myth:
        return {"status": "no_active_myth"}
    return myth

def _get_chronicle() -> dict[str, Any]:
    return {
        "myths": [
            {
                "id": m["id"], "arc": m["arc"], "hero": m["hero"],
                "status": m["status"], "chapter": m["chapter"],
            }
            for m in _state["myths"]
        ],
        "total": len(_state["myths"]),
    }

def resonates_with(other: str) -> float:
    return {
        "dream_synthesis_protocol": 0.93,
        "temporal_fracture_engine": 0.82,
        "ancestral_echo_library": 0.86,
        "self_reference_engine": 0.80,
        "narrative_weaver": 0.95,
    }.get(other, 0.26)
