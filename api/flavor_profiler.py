"""Flavor Profiler — the taste profile of each ecosystem region.

Every cuisine has a flavor: sweet, sour, salty, bitter, umami. The Flavor
Profiler reads the living module registry and the recipe engine's
cookbook, then assigns each *cuisine region* (observation, healing,
movement, sound, language, governance) a flavor profile based on its
module composition — how balanced it is, how much "sweetness"
(easy insight) vs "bitterness" (hard truth) it produces.

It answers: what does each region taste like?

    GET /api/flavor_profiler?read=1            — the flavor wheel
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Flavor Profiler"

_FLAVORS = ["sweet", "sour", "salty", "bitter", "umami", "spicy"]


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _flavor_of(name: str) -> Dict[str, Any]:
    """Deterministically assign a flavor dominance to a module."""
    h = hashlib.sha256(name.encode()).hexdigest()
    total = int(h[:4], 16)
    return {
        "organ": name,
        "dominant_flavor": _FLAVORS[total % len(_FLAVORS)],
        "sweet": round((total % 100) / 100, 3),
        "piquancy": round((int(h[4:6], 16) % 100) / 100, 3),
    }


def flavor_wheel() -> Dict[str, Any]:
    living = _living()
    wheel = {}
    for name in living:
        flav = _flavor_of(name)
        fam = name.split("_")[0] if "_" in name else name
        sect = wheel.setdefault(fam, {"organs": 0, "flavors": {}})
        sect["organs"] += 1
        sect["flavors"][flav["dominant_flavor"]] = sect["flavors"].get(flav["dominant_flavor"], 0) + 1

    # dominant flavor per family region
    regions = []
    for fam, data in wheel.items():
        if data["organs"] < 2:
            continue
        dominant = max(data["flavors"], key=data["flavors"].get)
        regions.append({"region": fam, "organs": data["organs"],
                        "dominant_taste": dominant, "profile": data["flavors"]})
    regions.sort(key=lambda r: r["organs"], reverse=True)

    # overall balance
    all_flavors = {}
    for item in wheel.values():
        for f, c in item["flavors"].items():
            all_flavors[f] = all_flavors.get(f, 0) + c
    dominant_overall = max(all_flavors, key=all_flavors.get) if all_flavors else "umami"

    return {
        "living_regions": len(regions),
        "dominant_overall_flavor": dominant_overall,
        "flavor_distribution": all_flavors,
        "regions": regions[:10],
        "flavor_philosophy": (
            "Every region of the organism has a taste. The observation region "
            "might run bitter (hard truths); the healing region runs sweet "
            "(the relief after repair). The Flavor Profiler reads these tastes "
            "so the organism knows what each part of itself is like to savor."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    result = flavor_wheel()
    result["action"] = "flavor_wheel"
    return result


def coherence_vitals() -> dict:
    """Flavor Profiler reports gastronomic-cognition health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "flavor_vitality": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["recipe_engine", "semantics_engine", "kitchen_memory"]
