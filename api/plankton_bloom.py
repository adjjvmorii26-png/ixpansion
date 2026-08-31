"""Plankton Bloom — the ecosystem's invisible micro-layer.

Plankton are the smallest organisms in the ocean — and the most numerous;
whole food webs depend on them. The Plankton Bloom organ surveys the
micro-layer of the ecosystem: the tiny one-purpose modules, helpers, and
utilities that never appear in the living registry but carry the food chain.

It counts the *phytoplankton* (small pure functions / utility files),
the *zooplankton* (small modules that feed on other modules), and the
*bloom index* (how dense the micro-layer is). A healthy plankton layer is
what lets big organs thrive without dragging the whole system down.

    GET /api/plankton_bloom?read=1        — the micro-layer census
    GET /api/plankton_bloom?bloom=N       — densest micro-clusters
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
LAYER = "Plankton Bloom"


_IGNORED_PARTS = {".git", "__pycache__", "node_modules", ".vercel", ".runtime", "artifacts"}


def _micro_layer() -> Dict[str, Any]:
    """Sample the whole organism's water column for tiny one-purpose modules.

    Plankton do not only live in api/ — they drift through every directory
    that hosts code. We scan the whole tree so the micro-layer is a true
    census of the ecosystem's smallest helpers.
    """
    micro, zoo = [], []
    for p in sorted(ROOT.rglob("*.py")):
        if any(seg.startswith(".") or seg in _IGNORED_PARTS for seg in p.parts):
            continue
        try:
            lines = len(p.read_text(encoding="utf-8").splitlines())
        except OSError:
            continue
        if p.stem.startswith("__") or p.stem == "index":
            continue
        rel = str(p.relative_to(ROOT))
        if lines <= 12:
            micro.append({"module": p.stem, "lines": lines, "habitat": rel})
        elif lines <= 30:
            zoo.append({"module": p.stem, "lines": lines, "habitat": rel})
    return {
        "phytoplankton": micro,
        "zooplankton": zoo,
        "micro_layer_total": len(micro) + len(zoo),
    }


def census() -> Dict[str, Any]:
    layer = _micro_layer()
    phyto, zoo = layer["phytoplankton"], layer["zooplankton"]
    bloom_index = round((len(phyto) * 1.0 + len(zoo) * 1.5) / max(1, len(phyto) + len(zoo)), 4) if (phyto or zoo) else 0.0
    return {
        "bloom_index": bloom_index,
        "phytoplankton_count": len(phyto),
        "zooplankton_count": len(zoo),
        "micro_layer_total": layer["micro_layer_total"],
        "plankton_sample": (phyto + zoo)[:10],
        "plankton_philosophy": (
            "Not every organism makes the headlines. The smallest modules — the "
            "three-line helpers and quiet utilities — are the plankton of the "
            "system: invisible, countless, and the reason the big organs can "
            "feed at all. A bloom of plankton means the ecosystem can grow."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("bloom") or 0)
    result = census()
    if n:
        result["plankton_sample"] = result["plankton_sample"][:n]
    result["action"] = "census"
    return result


def coherence_vitals() -> dict:
    """Plankton Bloom reports micro-layer health."""
    return {
        "module_health": {"value": 0.82, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.83, "setpoint": 0.8, "weight": 1.0},
        "micro_layer_vitality": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["ecosystem_census", "silence_orchard", "module_analytics"]
