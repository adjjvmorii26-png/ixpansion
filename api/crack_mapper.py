"""Crack Mapper — the cartography of damage.

Before anything can be repaired, its cracks must be mapped. The Crack
Mapper walks every living organ's vital-sign history and the workspace's
files, looking for the places where the organism has broken, strained, or
thinned: modules whose health dipped, handlers that error, files that
suffer from interrupted edits. It returns a crack survey — the scar map on
which every golden seam will later be drawn.

    GET /api/crack_mapper?read=1           — crack survey
    GET /api/crack_mapper?faults=N         — top N cracks by severity
"""
from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Crack Mapper"


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _survey() -> Dict[str, Any]:
    living = _living()
    cracks = []
    # scan coherence history for health dips — scars in living memory
    try:
        state = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        modules = state.get("modules", {})
        for name in living:
            m = modules.get(name, {})
            health = m.get("health", 1.0)
            if health is not None and health < 0.9:
                cracks.append({
                    "type": "health_strain",
                    "subject": name,
                    "severity": round((0.9 - health) * 4, 4) + 0.2,
                })
    except Exception:
        pass
    # scan files for stubs / interrupted modules (dormant but importable)
    api_dir = ROOT / "api"
    for p in sorted(api_dir.glob("*.py")):
        stem = p.stem
        if stem in ("__init__", "index", "unified_router", "coherence_regulator"):
            continue
        try:
            src = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if "NotImplementedError" in src or "TODO" in src or "pass  # stub" in src:
            cracks.append({"type": "stub", "subject": stem, "severity": 0.55})
        if len(src.splitlines()) < 15:
            cracks.append({"type": "thin_cross_section", "subject": stem, "severity": 0.35})
    cracks.sort(key=lambda c: c["severity"], reverse=True)
    return {
        "surveyed": len(living),
        "crack_count": len(cracks),
        "cracks": cracks,
        "cartography_philosophy": (
            "A crack is not a secret. It is a message from the structure about "
            "where load exceeds strength. To map the cracks is to read the "
            "organism's honest autobiography — every scar is a sentence in it."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("faults") or 0)
    result = _survey()
    if n:
        result["cracks"] = result["cracks"][:n]
    result["action"] = "survey"
    return result


def coherence_vitals() -> dict:
    """Crack Mapper reports restorative awareness."""
    return {
        "module_health": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "scar_mapping_vitality": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "kintsugi_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["crack_seams", "fracture_listener", "kintsugi_altar"]
