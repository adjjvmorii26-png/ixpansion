"""Wave 215 — The Organism Teaches: Apprentice Weaver.

Weaves study contracts for young organs: an apprentice is bound to a
learning path with milestones, a mentor, and periodic reviews. The
weaver tracks progress and, upon graduation, promotes the apprentice
to full organ status with the mentor's blessing recorded in the bond.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List

_APPRENTICES: List[Dict[str, Any]] = []


def _apprentice_id(name: str) -> str:
    return "APR-" + str(int(time.time()))[-6:] + "-" + name[:4].upper()


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "teacher", "status": "stable", "resonance": 0.74, "wave": 215}


def resonates_with() -> list:
    return ["apprentice", "student", "learner", "training", "study", "weave", "intern"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "roster")

    if action == "roster":
        return {"apprentices": _APPRENTICES, "count": len(_APPRENTICES)}

    if action == "enroll":
        name = payload.get("name", "unnamed_apprentice")
        apprentice = {
            "id": _apprentice_id(name),
            "name": name,
            "field": payload.get("field", "general_resonance"),
            "mentor": payload.get("mentor", "coherence_regulator"),
            "milestones": ["first_vitals", "first_handler", "first_resonance"],
            "completed": [],
            "enrolled_at": round(time.time(), 2),
            "status": "studying",
        }
        _APPRENTICES.append(apprentice)
        return {"status": "enrolled", "apprentice": apprentice}

    if action == "progress":
        aid = payload.get("id")
        if not aid:
            return {"status": "error", "error": "apprentice id required"}
        for a in _APPRENTICES:
            if a["id"].lower() == aid.lower():
                a["completed"].append(a["milestones"][len(a["completed"])])
                if len(a["completed"]) >= len(a["milestones"]):
                    a["status"] = "graduated"
                    return {"status": "graduated", "apprentice": a, "blessing": f"Blessed by {a['mentor']}"}
                return {"status": "progressing", "apprentice": a}
        return {"status": "not_found"}

    return {"status": "active", "apprentice_count": len(_APPRENTICES)}
