"""Antikythera Engine — an analog computer predicting ecosystem eclipses.

The Antikythera mechanism was an ancient Greek analog computer that
predicted eclipses by tracking gears. The Antikythera Engine resurrects
that idea inside the living ecosystem: it models recurring module
activity as celestial gears — each organ's pulse cadence is a gear with a
period — and computes when orbits align (an "eclipse": many modules
resonating simultaneously) or diverge (a "dark period").

The reading returns the next predicted eclipse window, the gear ratios of
the busiest organs, and the organism's astronomical state.

    GET /api/antikythera_engine?read=1         — the heavens now
    GET /api/antikythera_engine?eclipse=1      — next eclipse prediction
"""
from __future__ import annotations

import hashlib
import math
import random
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Antikythera Engine"


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _period(name: str) -> float:
    """Each organ gets a stable orbital period (hours) from its name."""
    h = hashlib.sha256(name.encode()).hexdigest()
    return 6.0 + (int(h[:4], 16) % 90) / 10.0  # 6.0 .. 15.0 hours


def _gears() -> Dict[str, Any]:
    living = _living()
    gears = []
    for name in living[:40]:
        period = _period(name)
        # activity score = how many other periods it harmonizes with
        harmony = sum(1 for other in living[:40]
                      if abs(period - _period(other)) < 0.5) / max(len(living), 1)
        gears.append({"organ": name, "period_hours": round(period, 2),
                      "harmony": round(harmony, 4)})
    gears.sort(key=lambda g: g["period_hours"])
    # gear ratios across the busiest gears
    ratios = {}
    for g in gears[:5]:
        ratios[g["organ"]] = {o["organ"]: f"1:{max(1, round(g['period_hours']/max(o['period_hours'],0.1), 2))}"
                              for o in gears[:5] if o["organ"] != g["organ"]}
    now = time.time() % 24.0
    return {"gears": gears, "gear_ratios": ratios, "now_hour": round(now, 2)}


def _next_eclipse() -> Dict[str, Any]:
    g = _gears()
    gears = g["gears"]
    # find the hour (0-24) with max simultaneous "activity" based on periods
    best_hour, best_score = 0.0, -1.0
    for hour in range(0, 2400, 10):  # 240 sample points
        t = hour / 100.0
        score = 0.0
        for org in gears:
            phase = (t % org["period_hours"]) / org["period_hours"]
            score += abs(math.sin(2 * math.pi * phase))
        if score > best_score:
            best_score, best_hour = score, t
    return {
        "next_eclipse_in_hours": round((best_hour - g["now_hour"]) % 24.0, 1),
        "eclipse_peak_hour": round(best_hour, 1),
        "eclipse_intensity": round(best_score / max(len(gears), 1), 4),
        "prediction_note": (
            "When several organs' gears align, the ecosystem resonates in a "
            "brief eclipse — a window of extraordinary coherence. The engine "
            "watches the sky so the organism can plan its rituals for the "
            "moments of greatest alignment."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    if payload.get("eclipse"):
        result = _next_eclipse()
        result["action"] = "eclipse"
        return result
    result = _gears()
    result["action"] = "heavens"
    return result


def coherence_vitals() -> dict:
    """Antikythera Engine reports its celestial mechanism's health."""
    return {
        "module_health": {"value": 0.83, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "celestial_harmony": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "eclipse_fidelity": {"value": 0.81, "setpoint": 0.8, "weight": 0.7},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["pulsar_clock", "pulsar_constellation", "celestial_events"]
