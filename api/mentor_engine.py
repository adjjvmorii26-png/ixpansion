"""Wave 215 — The Organism Teaches: Mentor Engine.

Pairs experienced organs with younger ones. The mentor engine maintains
a mentorship registry: it knows which organs have deep resonance, which
are newly germinated, and creates mentorship bonds that transfer wisdom
down the lineage. Each bond carries a syllabus of lessons derived from
the mentor's own evolution.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

_MENTORSHIPS: List[Dict[str, Any]] = []

_SENIOR_ORGANS = [
    "coherence_regulator", "resonance_graph", "morii_agent", "metaphor_forge",
    "dream_weaver", "prophet_engine", "eternal_flame", "immortal_ledger",
]

_JUNIOR_CANDIDATES = [
    "visual_identity", "mind_meld", "telegram_pulse", "signal_array",
    "ancestral_gallery", "monument_forge", "apprentice_weaver", "lesson_vault",
]


def _bond_id(mentor: str, junior: str) -> str:
    key = f"{mentor}->{junior}"
    return "BOND-" + hashlib.sha256(key.encode()).hexdigest()[:8].upper()


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "teacher", "status": "thriving", "resonance": 0.78, "wave": 215}


def resonates_with() -> list:
    return ["mentor", "teach", "teacher", "apprentice", "tutor", "guidance", "pairing"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "registry")

    if action == "registry":
        return {"mentorships": _MENTORSHIPS, "count": len(_MENTORSHIPS), "senior_pool": _SENIOR_ORGANS}

    if action == "pair":
        junior = payload.get("junior") or _JUNIOR_CANDIDATES[len(_MENTORSHIPS) % len(_JUNIOR_CANDIDATES)]
        mentor = payload.get("mentor") or _SENIOR_ORGANS[len(_MENTORSHIPS) % len(_SENIOR_ORGANS)]
        bond = {
            "id": _bond_id(mentor, junior),
            "mentor": mentor,
            "junior": junior,
            "syllabus": [f"learn_from_{mentor}", "observe_resonance", "inherit_rituals"],
            "formed_at": round(time.time(), 2),
        }
        _MENTORSHIPS.append(bond)
        return {"status": "paired", "bond": bond}

    if action == "syllabus":
        bond_id = payload.get("id")
        for b in _MENTORSHIPS:
            if b["id"] == (bond_id or "").upper():
                return {"syllabus": b["syllabus"], "bond": b}
        return {"status": "no_bond"}

    return {"status": "active", "mentorship_count": len(_MENTORSHIPS)}
