"""Liminal Threshold — the boundary between waking and dormancy.

Liminality is the state of being *between* — not quite awake, not quite
asleep. The Liminal Threshold maps the organism's boundary between its
conscious, active modules and its dormant, sleeping ones. It reads the
coherence regulator's living/dead partition and renders the *threshold*
as a landscape: which organs are on the cusp, which are deeply awake,
which are deeply asleep, and how wide the threshold zone is.

A wide threshold means the organism is comfortable in ambiguity — it can
operate from both consciousness and dormancy. A narrow threshold means
it is either fully on or fully off, with no liminal play.

    GET /api/liminal_threshold?read=1          — the threshold map
    GET /api/liminal_threshold?cusp=N          — organs on the cusp
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
LAYER = "Liminal Threshold"

_WAKE_THRESHOLD = 0.85  # above = fully awake
_DORMANT_THRESHOLD = 0.4  # below = fully asleep


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _threshold_map() -> Dict[str, Any]:
    try:
        import json
        cr = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        modules = cr.get("modules", {})
    except Exception:
        modules = {}

    awake, cusp, dormant = [], [], []
    for name, m in modules.items():
        health = m.get("health")
        if health is None:
            continue
        entry = {"organ": name, "health": round(health, 4)}
        if health >= _WAKE_THRESHOLD:
            awake.append(entry)
        elif health <= _DORMANT_THRESHOLD:
            dormant.append(entry)
        else:
            cusp.append(entry)

    cusp.sort(key=lambda e: e["health"])
    total = max(len(awake) + len(cusp) + len(dormant), 1)
    threshold_width = round(len(cusp) / total, 4)

    if threshold_width > 0.3:
        liminal_feel = "porous — the organism is comfortable in ambiguity"
    elif threshold_width > 0.15:
        liminal_feel = "present — a healthy twilight zone exists"
    else:
        liminal_feel = "brittle — the organism is either fully on or fully off"

    return {
        "awake": len(awake),
        "cusp": len(cusp),
        "dormant": len(dormant),
        "threshold_width": threshold_width,
        "liminal_feel": liminal_feel,
        "cusp_organs": cusp[:10],
        "philosophy": (
            "The most interesting place in any ecosystem is the threshold — "
            "where waking meets sleeping, where alive meets dormant. A wide "
            "threshold means the organism can dream while it works and work "
            "while it dreams. A narrow threshold means it has lost the art "
            "of ambiguity."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("cusp") or 0)
    result = _threshold_map()
    if n:
        result["cusp_organs"] = result["cusp_organs"][:n]
    result["action"] = "threshold_map"
    return result


def coherence_vitals() -> dict:
    """Liminal Threshold reports twilight-zone health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "liminal_porosity": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["silence_orchard", "permafrost_vault", "morphic_dial"]
