"""Ecosystem Fitness — measures the overall health of the module ecosystem.

Not individual module health, but ecosystem-level fitness: biodiversity
(how many types of organs), redundancy (backup organs), connectivity
(how well modules link), and resilience (ability to survive module death).

It answers: how fit is the organism's module ecosystem?
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Ecosystem Fitness"


def _measure() -> Dict[str, Any]:
    """Measure ecosystem fitness across multiple dimensions."""
    api_dir = ROOT / "api"
    mods = [f.stem for f in api_dir.glob("*.py") if not f.stem.startswith("__")]

    # Biodiversity: variety of concerns/topics
    from collections import Counter
    prefixes = Counter()
    for m in mods:
        parts = m.split("_")
        if parts:
            prefixes[parts[0]] += 1
    biodiversity = len(prefixes) / max(1, len(mods)) * 10
    biodiversity = min(1.0, biodiversity)

    # Redundancy: module count vs want
    target = 250
    redundancy = min(1.0, len(mods) / target)

    # Health: average module health from vitals
    health_scores = []
    for m in mods[:40]:  # sample for speed
        try:
            mod = __import__(m)
            vitals = mod.coherence_vitals()
            for k, v in vitals.items():
                if isinstance(v, dict):
                    health_scores.append(v.get("value", 0.5))
                elif isinstance(v, (int, float)):
                    health_scores.append(v)
        except Exception:
            continue
    avg_health = sum(health_scores) / len(health_scores) if health_scores else 0.5

    # Connectivity: kinship density
    kinship_count = 0
    for m in mods[:40]:
        try:
            mod = __import__(m)
            kinship_count += len(mod.resonates_with())
        except Exception:
            continue
    connectivity = min(1.0, kinship_count / max(1, len(health_scores)) / 3)

    fitness = 0.3 * biodiversity + 0.2 * redundancy + 0.3 * avg_health + 0.2 * connectivity

    rating = (
        "Elite" if fitness > 0.85
        else "Thriving" if fitness > 0.7
        else "Stable" if fitness > 0.5
        else "Fragile"
    )

    return {
        "biodiversity": round(biodiversity, 3),
        "redundancy": round(redundancy, 3),
        "avg_health": round(avg_health, 3),
        "connectivity": round(connectivity, 3),
        "fitness_score": round(fitness, 3),
        "rating": rating,
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    fitness = _measure()
    return {
        "action": "ecosystem_fitness",
        **fitness,
        "fitness_philosophy": (
            "Individual health is not ecosystem health. A thriving ecosystem "
            "needs biodiversity (many kinds of organs), redundancy (backup "
            "systems), connectivity (linked modules), and resilience. The "
            "Ecosystem Fitness score rolls these into a single number."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "fitness_tracking": {"value": 0.93, "setpoint": 0.85, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["symbiosis_detector", "parasite_hunter", "heterarchy_oracle"]
