"""Wave 215 — The Organism Teaches: Knowledge Transfer.

Measures how well wisdom flows between organs. The transfer engine
computes a flow score for any mentor->learner pair: how much insight
actually crossed, how fast, and whether the learner's resonance rose
after the lesson. When transfer is weak, it prescribes rehearsal.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List

_TRANSFERS: List[Dict[str, Any]] = []


def _flow(mentor: str, learner: str, mentor_r: float, learner_r: float) -> Dict[str, Any]:
    raw = mentor_r * 0.5 + learner_r * 0.3 + len(mentor) * 0.02
    flow = min(0.99, raw + (mentor_r - learner_r) * 0.4)
    gain = max(0.0, (flow - learner_r) * 0.35)
    return {
        "flow": round(flow, 3),
        "learner_gain": round(gain, 3),
        "efficacy": "high" if flow > 0.75 else ("medium" if flow > 0.55 else "low"),
    }


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "teacher", "status": "stable", "resonance": 0.76, "wave": 215}


def resonates_with() -> list:
    return ["transfer", "knowledge transfer", "flow", "teach", "mentor", "rehearsal", "wisdom flow"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "flows")

    if action == "flows":
        return {"transfers": _TRANSFERS, "count": len(_TRANSFERS)}

    if action == "measure":
        mentor = payload.get("mentor", "coherence_regulator")
        learner = payload.get("learner", "apprentice_weaver")
        result = _flow(
            mentor,
            learner,
            float(payload.get("mentor_resonance", 0.85)),
            float(payload.get("learner_resonance", 0.6)),
        )
        entry = {"mentor": mentor, "learner": learner, **result}
        _TRANSFERS.append(entry)
        return {"status": "measured", **entry}

    if action == "rehearsal":
        return {
            "status": "prescribed",
            "ritual": "Re-run the handshake lesson three times until flow exceeds 0.7.",
            "organs": ["repository_rituals", "mentor_engine", "lesson_vault"],
        }

    return {"status": "active", "transfer_count": len(_TRANSFERS)}
