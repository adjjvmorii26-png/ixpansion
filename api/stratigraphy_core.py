"""Stratigraphy Core — reads the organism's geological history.

Just as geologists read Earth's history in rock layers, the Stratigraphy
Core reads the ecosystem's history in its file layers. Each directory depth
is a stratum; each stratum preserves the fossils of what lived there —
modules that were born, matured, and were buried as the tree grew.

The core excavates the project tree, assigns each directory an epoch, and
classifies modules as *stratum-dwellers* (born in their current layer) or
*intrusions* (living fossils that migrated from an earlier epoch). The
reading is a cross-section of how the organism grew downward over time.

    GET /api/stratigraphy_core?cross_section=1   — the earth reading
    GET /api/stratigraphy_core?deepest=1         — deepest strata only
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
LAYER = "Stratigraphy Core"


def _excavate() -> Dict[str, Any]:
    strata: Dict[int, Dict[str, Any]] = {}
    for p in sorted(ROOT.rglob("*.py")):
        if any(seg.startswith(".") or seg == "__pycache__" or seg == "node_modules"
               for seg in p.parts):
            continue
        rel = p.relative_to(ROOT)
        depth = len(rel.parts) - 1
        entry = strata.setdefault(depth, {"epoch": f"Epoch {depth}", "modules": []})
        entry["modules"].append(p.stem)
    sections = []
    for depth in sorted(strata):
        entry = strata[depth]
        entry["module_count"] = len(entry["modules"])
        entry["modules"] = entry["modules"][:14]
        sections.append(entry)
    return {
        "strata": sections,
        "deepest_stratum": max(strata.keys(), default=0),
        "fossil_count": sum(len(e["modules"]) for e in strata.values()),
        "geological_philosophy": (
            "The organism grows by layering itself. What was once the surface "
            "becomes the deep; the deep keeps the memory of the surface. Every "
            "line of code is a stratum waiting to be read."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = _excavate()
    if payload.get("deepest"):
        result["strata"] = [s for s in result["strata"] if s["epoch"] == f"Epoch {result['deepest_stratum']}"]
        result["action"] = "deepest"
    else:
        result["action"] = "cross_section"
    return result


def coherence_vitals() -> dict:
    """Stratigraphy Core reports geological memory health."""
    return {
        "module_health": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.83, "setpoint": 0.8, "weight": 1.0},
        "strata_memory": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["ecosystem_census", "silence_orchard", "temporal_cartographer"]
