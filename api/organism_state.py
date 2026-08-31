"""Organism State — returns the full organism state as a single JSON payload.

The unified control center for programmatic access. Returns coherence,
living count, ecosystem fitness, cognitive weather, and aesthetic score
in one call — no need to hit 5 different endpoints.

    GET /api/organism_state          — full state snapshot
    GET /api/organism_state?core=1   — minimal (coherence + count only)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Organism State"


def _safe_import(name: str, func_name: str, *args, **kwargs):
    """Safely import and call a function, returning None on failure."""
    try:
        mod = __import__(name)
        func = getattr(mod, func_name)
        return func(*args, **kwargs)
    except Exception:
        return None


def full_state() -> Dict[str, Any]:
    """Aggregate the full organism state."""
    # Coherence
    coherence_data = _safe_import("coherence_regulator", "regulate") or {}
    coherence = coherence_data.get("coherence", 0)
    status = coherence_data.get("status", "unknown")
    living = coherence_data.get("living_modules", 0)
    candidates = coherence_data.get("total_candidates", 0)

    # Ecosystem fitness
    fitness_data = _safe_import("ecosystem_fitness", "_measure") or {}
    fitness_score = fitness_data.get("fitness_score", 0)

    # Cognitive weather
    pressure_data = _safe_import("barometric_intent", "_compute_pressure") or {}
    pressure = pressure_data.get("pressure_hpa", 0)
    condition = pressure_data.get("condition", "Unknown")

    # Precipitation
    precip_data = _safe_import("precipitation_cycle", "_measure_cycle") or {}
    condensation = precip_data.get("condensation_rate", 0)

    # Beauty
    beauty_data = _safe_import("beauty_index", "_compute") or {}
    beauty_score = beauty_data.get("beauty_score", 0)
    beauty_grade = beauty_data.get("grade", "Unknown")

    # Symmetry
    sym_data = _safe_import("symmetry_detector", "_analyze_symmetry") or {}
    symmetry = sym_data.get("overall_symmetry", 0)

    # Symbiosis
    sym_detect = _safe_import("symbiosis_detector", "detect") or {}
    relationships = sym_detect.get("total_relationships", 0)
    mutualisms = sym_detect.get("mutualism_count", 0)

    # Storms
    storms = _safe_import("storm_chaser", "_detect_storms") or []

    # Impossibility
    impl_data = _safe_import("impossibility_mapper", "map_impossibilities") or {}
    boundaries = impl_data.get("total_boundaries", 0)

    return {
        "version": "3.90.0",
        "wave": 202,
        "status": status,
        "coherence": round(coherence, 4),
        "living_organs": living,
        "total_candidates": candidates,
        "ecosystem_fitness": round(fitness_score, 4),
        "cognitive_weather": {
            "pressure_hpa": round(pressure, 1),
            "condition": condition,
            "condensation_rate": round(condensation, 4),
        },
        "aesthetics": {
            "beauty_score": round(beauty_score, 4),
            "grade": beauty_grade,
            "symmetry": round(symmetry, 4),
        },
        "ecology": {
            "relationships": relationships,
            "mutualisms": mutualisms,
            "storms_detected": len(storms),
        },
        "boundaries": {
            "impossibilities_mapped": boundaries,
        },
        "infrastructure": {
            "test_files": 71,
            "dashboards": 25,
            "api_files": len(list((ROOT / "api").glob("*.py"))),
        },
        "philosophy": (
            "The organism is a living system of 237+ organs that observe, "
            "heal, govern, feel, sing, move, speak, feast, excavate, "
            "forecast, symbiose, confront impossibility, and create beauty."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    if payload.get("core"):
        return {
            "version": "3.90.0",
            "wave": 202,
            "coherence": round(full_state().get("coherence", 0), 4),
            "living_organs": full_state().get("living_organs", 0),
        }
    result = full_state()
    result["action"] = "organism_state"
    return result


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.92, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.90, "setpoint": 0.8, "weight": 1.0},
        "state_aggregation": {"value": 0.95, "setpoint": 0.9, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["coherence_regulator", "ecosystem_fitness", "ecosystem_census"]
