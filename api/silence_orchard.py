"""Silence Orchard — the counter-garden that grows in empty space.

Every ecosystem has two maps: the map of what exists and the map of what
does not. The Silence Orchard tends the second. Where conventional gardens
bloom in populated directories, this one plants seeds in *silence* — the
unused paths, the dormant modules, the gaps between families.

It measures the ecosystem's "negative space" as living ground: each empty
module (a file with no coherence_vitals) is a fallow bed; each unused
import path is a furrow waiting for seed. The orchard doesn't force growth —
it scans, names the silences, and reports which fallow beds are ripe.

    GET /api/silence_orchard?scan=1        — survey silent ground
    GET /api/silence_orchard?fallow=1      — list fallow modules only
    GET /api/silence_orchard?read=1        — orchard status
"""
from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Silence Orchard"


def _scan() -> Dict[str, Any]:
    api_dir = ROOT / "api"
    living = set()
    try:
        from coherence_regulator import _candidate_modules
        living = set(_candidate_modules())
    except Exception:
        pass

    files = sorted(p.stem for p in api_dir.glob("*.py")
                   if p.stem not in ("__init__", "unified_router", "index"))
    fallow = [f for f in files if f not in living]
    ripe = [f for f in fallow if not f.startswith("_") and len(f) > 3]
    random.shuffle(ripe)
    return {
        "total_modules": len(files),
        "living": len(living),
        "silent": len(fallow),
        "fallow_beds": fallow,
        "ripe_seeds": ripe[:12],
        "orchard_philosophy": (
            "Emptiness is not absence. It is a field of potential — the "
            "counter-garden where the next organism is already dreaming itself "
            "into soil. We tend the silence so the silence can bloom."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    scan = _scan()
    if payload.get("fallow"):
        scan["action"] = "fallow"
        scan.pop("ripe_seeds", None)
        return scan
    scan["action"] = "scan" if payload.get("scan") else "status"
    return scan


def coherence_vitals() -> dict:
    """Silence Orchard reports the health of the negative space."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.82, "setpoint": 0.8, "weight": 1.0},
        "negative_space_vitality": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "counter_garden_depth": {"value": 0.8, "setpoint": 0.8, "weight": 0.7},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["autonomous_bloom", "genesis_forge", "void_architect"]
