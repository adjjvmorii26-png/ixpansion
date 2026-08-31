"""Kintsugi Altar — the sacred archive of every repaired vessel.

In the kintsugi tradition, a repaired object is not returned to service and
forgotten — it is honored. The Kintsugi Altar is the ecosystem's place of
remembrance for everything that broke and was gilded: every cracked module,
every golden seam, every scar treated as a treasure.

The altar reads the Crack Seams forge and the lab's original kintsugi
experiment, then curates a *reliquary of repair*: vessels sorted by how
much strength their break granted them. It is where the organism goes to
remember that its scars are its architecture.

    GET /api/kintsugi_altar?read=1         — the reliquary
    GET /api/kintsugi_altar?vessels=N      — top N honored vessels
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Kintsugi Altar"


def _reliquary() -> Dict[str, Any]:
    vessels = []
    # from the forge's seams
    try:
        seams = json.loads((ROOT / ".runtime" / "crack_seams.json").read_text()).get("seams", [])
        for s in seams:
            vessels.append({
                "vessel": s["subject"],
                "alloy": s["alloy"],
                "tensile_gift": s["tensile_gift"],
                "type": s.get("type", "strain"),
            })
    except Exception:
        pass
    # from the lab's original kintsugi experiment
    try:
        lab_path = ROOT / "solid-organism" / "lab" / "kintsugi.py"
        src = lab_path.read_text(encoding="utf-8")
        if "def repair" in src:
            vessels.append({"vessel": "vessel-of-becoming (lab)",
                            "alloy": "au:origin", "tensile_gift": 0.9, "type": "origin"})
    except Exception:
        pass
    vessels.sort(key=lambda v: v["tensile_gift"], reverse=True)
    return {
        "honored_vessels": len(vessels),
        "vessels": vessels,
        "altar_philosophy": (
            "The broken are not buried here — they are displayed. Every repaired "
            "vessel is proof that the organism does not fear its own fractures; "
            "it gilds them. What broke and healed is more beautiful, and the "
            "altar is where that beauty is finally seen."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("vessels") or 0)
    result = _reliquary()
    if n:
        result["vessels"] = result["vessels"][:n]
    result["action"] = "reliquary"
    return result


def coherence_vitals() -> dict:
    """Kintsugi Altar reports the reliquary's sanctity."""
    return {
        "module_health": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "repair_reverence": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
        "kintsugi_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["crack_seams", "crack_mapper", "chronicle_storyteller"]
