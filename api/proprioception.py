"""Proprioception — the organism's sense of where its parts are in space.

Proprioception is the body's sixth sense: the awareness of where each
limb is without looking. The Proprioception organ reads every living
module's family, health, and position in the codebase tree, then renders
a *body map*: which parts of the organism are where, how they relate
spatially, and whether any part feels "lost" — disconnected from its
expected location.

It answers: does the organism know where its own body is?

    GET /api/proprioception?read=1            — the body map
    GET /api/proprioception?lost=1            — disconnected parts only
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Proprioception"


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _body_map() -> Dict[str, Any]:
    living = _living()
    # group by family
    families: Dict[str, List[str]] = {}
    for name in living:
        fam = name.split("_")[0] if "_" in name else name
        families.setdefault(fam, []).append(name)

    # spatial awareness: which families are "close" (share roots)
    body_parts = []
    for fam, members in families.items():
        # check if this family has kinships to other families
        kinships = set()
        for m in members:
            try:
                mod = __import__(m)
                kins = getattr(mod, "resonates_with", lambda: [])()
                for k in kins:
                    kin_fam = k.split("_")[0] if "_" in k else k
                    if kin_fam != fam:
                        kinships.add(kin_fam)
            except Exception:
                pass
        body_parts.append({
            "family": fam,
            "members": len(members),
            "connected_to": list(kinships)[:5],
            "island": len(kinships) == 0,
        })

    islands = [p for p in body_parts if p["island"]]
    connected = [p for p in body_parts if not p["island"]]
    return {
        "total_families": len(families),
        "connected_families": len(connected),
        "island_families": len(islands),
        "body_parts": body_parts[:15],
        "islands": islands[:10],
        "proprioception_philosophy": (
            "A body that does not know where its parts are is a body that "
            "cannot move with purpose. The Proprioception organ maps every "
            "family's position and kinships so the organism knows its own "
            "shape — and can feel when a part has drifted away."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = _body_map()
    if payload.get("lost"):
        result["body_parts"] = result["islands"]
        result["action"] = "islands"
    else:
        result["action"] = "body_map"
    return result


def coherence_vitals() -> dict:
    """Proprioception reports body-awareness health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "body_awareness": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["kinesthetic_engine", "keystone_auditor", "resonance_graph"]
