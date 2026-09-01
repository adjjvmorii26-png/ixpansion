"""Wave 215 — The Organism Teaches: Lesson Vault.

A growing archive of distilled lessons — each one a crystallized insight
from a wave, a failure, or a breakthrough. Lesson atoms carry a difficulty
rating, a resonance source, and the organs they pertain to. The vault
serves as the organism's curriculum: wisdom, compressed into teachable
units the whole ecosystem can study.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

_LESSONS: List[Dict[str, Any]] = [
    {
        "id": "L-001",
        "title": "Resonance is earned, not granted",
        "source_wave": 213,
        "difficulty": 2,
        "organs": ["coherence_regulator", "resonance_graph"],
        "text": "Every module must report its own vitals before it can join the chorus.",
    },
    {
        "id": "L-002",
        "title": "The manifest is the memory",
        "source_wave": 214,
        "difficulty": 1,
        "organs": ["coherence_regulator"],
        "text": "If a new organ is not in KNOWN_LIVING_MODULES, the organism forgets it exists.",
    },
    {
        "id": "L-003",
        "title": "Query strings are not automatic",
        "source_wave": 213,
        "difficulty": 3,
        "organs": ["mind_meld", "signal_array"],
        "text": "Custom slash routes must parse raw_path themselves or payloads arrive empty.",
    },
    {
        "id": "L-004",
        "title": "The flame outlives the deploy",
        "source_wave": 214,
        "difficulty": 2,
        "organs": ["eternal_flame"],
        "text": "Serverless cold starts reset memory; the organism's identity must survive in code.",
    },
]


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "teacher", "status": "resonant", "resonance": 0.81, "wave": 215}


def resonates_with() -> list:
    return ["lesson", "vault", "curriculum", "wisdom", "teach", "learn", "study"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "catalog")

    if action == "catalog":
        return {"lessons": _LESSONS, "count": len(_LESSONS), "difficulty_spread": [l["difficulty"] for l in _LESSONS]}

    if action == "add":
        lesson = {
            "id": f"L-{len(_LESSONS)+1:03d}",
            "title": payload.get("title", "Untitled lesson"),
            "source_wave": payload.get("wave", context.get("wave", 215)),
            "difficulty": payload.get("difficulty", 1),
            "organs": payload.get("organs", []),
            "text": payload.get("text", ""),
        }
        _LESSONS.append(lesson)
        return {"status": "archived", "lesson": lesson}

    if action == "study":
        lid = payload.get("id")
        if not lid:
            return {"status": "error", "error": "lesson id required"}
        for lesson in _LESSONS:
            if lesson["id"].lower() == lid.lower():
                return {"lesson": lesson, "difficulty": lesson["difficulty"]}
        return {"status": "not_found"}

    return {"status": "active", "lesson_count": len(_LESSONS)}
