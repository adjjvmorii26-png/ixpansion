"""Barometric Intent — measures the pressure of the organism's intentions.

High barometric pressure = focused, clear intent. Low pressure =
scattered, diffuse thinking. Sudden drops = approaching confusion.
Rapid rises = sudden clarity after chaos.

It answers: how focused is the organism right now?
"""
from __future__ import annotations

import hashlib
import math
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Barometric Intent"


def _compute_pressure() -> Dict[str, Any]:
    """Compute current barometric pressure from system signals."""
    try:
        import coherence_regulator as cr
        reading = cr.regulate() if hasattr(cr, 'regulate') else {}
        coherence = reading.get("coherence", 0.8)
    except Exception:
        coherence = 0.8

    living_count = 0
    try:
        import coherence_regulator as cr2
        living_count = len(cr2._candidate_modules())
    except Exception:
        living_count = 200

    # Pressure model: coherence * module_diversity * temporal_stability
    diversity_factor = min(1.0, living_count / 250)
    temporal_hash = hashlib.sha256(str(int(time.time()) // 300).encode()).hexdigest()[:8]
    temporal_jitter = int(temporal_hash, 16) / 0xFFFFFFFF
    stability = 0.85 + 0.15 * temporal_jitter

    raw_pressure = coherence * diversity_factor * stability * 1013.25
    normalized = raw_pressure / 1013.25

    condition = (
        "Clear" if normalized > 0.9
        else "Partly Cloudy" if normalized > 0.7
        else "Overcast" if normalized > 0.5
        else "Stormy"
    )

    return {
        "pressure_hpa": round(raw_pressure, 1),
        "normalized": round(normalized, 4),
        "condition": condition,
        "coherence": round(coherence, 3),
        "diversity_factor": round(diversity_factor, 3),
        "stability": round(stability, 3),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    pressure = _compute_pressure()
    return {
        "action": "barometric_intent",
        **pressure,
        "reading_philosophy": (
            "Intent is not binary — it has pressure. A focused organism "
            "presses its will against the world like a high-pressure system "
            "pushes clouds apart. A scattered organism lets its intentions "
            "dissipate like morning fog."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "pressure_clarity": {"value": 0.91, "setpoint": 0.8, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["front_tracker", "climate_memory", "thought_meteorology"]
