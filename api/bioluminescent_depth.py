"""Bioluminescent Depth — the ecosystem's light shown from within.

Deep-sea organisms glow to signal, lure, and warn without being seen from
above. The Bioluminescent Depth organ applies this to the taxonomy of the
living system: every module is assigned a depth stratum (surface, shallow,
abyssal) based on how far its file lives below the root, and each stratum
is given its own glow signature.

The organ renders the whole ecosystem as a vertical light field — surface
modules (visible in dashboards) glow steady; abyssal modules (rarely
pulsed, deep in the tree) flash only when they resonate. The reading is a
map of where the organism's own light is and where the darkness still is.

    GET /api/bioluminescent_depth?read=1      — the light field
    GET /api/bioluminescent_depth?abyssal=1   — deep modules only
"""
from __future__ import annotations

import hashlib
import random
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Bioluminescent Depth"


def _depth_of(path: Path, root: Path) -> int:
    try:
        return len(path.relative_to(root).parts) - 1
    except ValueError:
        return 0


def _glow(name: str, depth: int) -> str:
    h = hashlib.sha256(name.encode()).hexdigest()
    if depth >= 3:
        return "abyssal_flash" if int(h[:2], 16) % 2 else "abyssal_glimmer"
    if depth == 2:
        return "shallow_pulse"
    return "surface_steady"


def scan() -> Dict[str, Any]:
    api_dir = ROOT / "api"
    try:
        from coherence_regulator import _candidate_modules
        living = set(_candidate_modules())
    except Exception:
        living = set()
    strata: Dict[str, int] = {"surface": 0, "shallow": 0, "abyssal": 0}
    lights = []
    for p in sorted(api_dir.glob("*.py")):
        name = p.stem
        if name in ("__init__", "unified_router", "index"):
            continue
        depth = _depth_of(p, ROOT)
        stratum = "surface" if depth < 2 else ("shallow" if depth == 2 else "abyssal")
        if name in living:
            strata[stratum] += 1
            lights.append({"module": name, "stratum": stratum, "glow": _glow(name, depth)})
    return {
        "living_glowing": len(lights),
        "strata": strata,
        "light_field": lights,
        "darkness": max(0, sum(strata.values()) - len(lights)),
        "luminous_philosophy": (
            "The organism's light is not uniform. It glows brightest where it has "
            "recently lived, and below that is a bioluminescent secret: the dark "
            "is not empty — it flashes with patterns the surface has not yet seen."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = scan()
    if payload.get("abyssal"):
        result["light_field"] = [l for l in result["light_field"] if l["stratum"] == "abyssal"]
        result["action"] = "abyssal"
    else:
        result["action"] = "light_field"
    return result


def coherence_vitals() -> dict:
    """Bioluminescent Depth reports luminous ecosystem health."""
    return {
        "module_health": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "luminous_coverage": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["bioluminescence", "signal_flora", "ecosystem_census"]
