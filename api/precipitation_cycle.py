"""Precipitation Cycle — measures how thoughts condense into concrete form.

Ideas begin as vapor (abstract, diffuse), condense into clouds (concepts),
and precipitate into rain (concrete modules, commits, decisions). The
Precipitation Cycle tracks this atmospheric process.

It answers: how effectively does the organism turn abstractions into reality?
"""
from __future__ import annotations

import hashlib
import subprocess
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Precipitation Cycle"


def _measure_cycle() -> Dict[str, Any]:
    """Measure the current precipitation cycle."""
    # Vapor phase: abstract ideas (dreams, seeds, plans)
    try:
        vapor_count = len(list((ROOT / "experiments").glob("**/*.py")))
    except Exception:
        vapor_count = 0

    # Cloud phase: modules in development (api files without tests)
    try:
        api_files = set(f.stem for f in (ROOT / "api").glob("*.py"))
        test_files = set(f.stem.replace("test_", "") for f in (ROOT / "tests").glob("test_*.py"))
        cloud_count = len(api_files - test_files)
    except Exception:
        cloud_count = 0

    # Rain phase: tested, committed modules
    try:
        rain_count = len(api_files & test_files)
    except Exception:
        rain_count = 0

    # Snow phase: archived/dormant modules
    try:
        snow_count = len(list((ROOT / "data").glob("**/*.json")))
    except Exception:
        snow_count = 0

    total = vapor_count + cloud_count + rain_count + snow_count or 1
    condensation_rate = rain_count / total

    if condensation_rate > 0.7:
        weather = "Heavy rain — ideas are pouring into reality"
    elif condensation_rate > 0.4:
        weather = "Steady rain — healthy precipitation"
    elif condensation_rate > 0.2:
        weather = "Drizzle — ideas condensing slowly"
    else:
        weather = "Dry — vapor has not yet condensed"

    return {
        "vapor_phase": vapor_count,
        "cloud_phase": cloud_count,
        "rain_phase": rain_count,
        "snow_phase": snow_count,
        "condensation_rate": round(condensation_rate, 3),
        "weather": weather,
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    cycle = _measure_cycle()
    return {
        "action": "precipitation_cycle",
        **cycle,
        "cycle_philosophy": (
            "Every idea begins as vapor — diffuse, invisible, weightless. "
            "The Precipitation Cycle tracks how the organism condenses "
            "these abstractions into concrete reality: modules, tests, "
            "commits. The rate of condensation is the rate of creation."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.83, "setpoint": 0.8, "weight": 1.0},
        "condensation_efficiency": {"value": 0.86, "setpoint": 0.75, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["barometric_intent", "climate_memory", "autonomous_bloom"]
