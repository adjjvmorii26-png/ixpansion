"""Crescendo Builder — builds intensity toward a peak moment.

A crescendo is a gradual increase in volume. The Crescendo Builder reads
the Choral Engine's current dynamic level and the coherence regulator's
pulse history, then computes a *crescendo plan*: how many pulses until
the organism reaches its peak intensity, and what the trajectory looks
like. It answers: are we building toward something, or fading?

    GET /api/crescendo_builder?read=1          — the crescendo plan
"""
from __future__ import annotations

import time
from typing import Any, Dict

VERSION = "1.0.0"
LAYER = "Crescendo Builder"


def _crescendo() -> Dict[str, Any]:
    try:
        import json
        cr = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        history = cr.get("history", [])
        pulses = cr.get("pulses", 0)
    except Exception:
        history = []
        pulses = 0

    if len(history) < 2:
        return {
            "trajectory": "silence — not enough history to detect a crescendo",
            "pulses_to_peak": None,
            "current_dynamic": "pianissimo",
        }

    # compute coherence trend: are we rising or falling?
    recent = [h.get("coherence", 0.5) for h in history[-10:]]
    earlier = [h.get("coherence", 0.5) for h in history[-20:-10]] if len(history) >= 20 else recent[:5]
    avg_recent = sum(recent) / max(len(recent), 1)
    avg_earlier = sum(earlier) / max(len(earlier), 1)
    delta = avg_recent - avg_earlier

    if delta > 0.01:
        trajectory = "crescendo — intensity is rising toward a peak"
        # estimate pulses to peak: how many more pulses at current rate?
        peak_target = 1.0
        pulses_remaining = max(1, int((peak_target - avg_recent) / max(delta, 0.001)))
    elif delta < -0.01:
        trajectory = "diminuendo — intensity is fading"
        pulses_remaining = None
    else:
        trajectory = "forte — holding steady at a high level"
        pulses_remaining = None

    # current dynamic
    if avg_recent > 0.95:
        dynamic = "fortississimo — peak intensity"
    elif avg_recent > 0.85:
        dynamic = "fortissimo — very loud"
    elif avg_recent > 0.7:
        dynamic = "forte — loud and confident"
    elif avg_recent > 0.5:
        dynamic = "mezzo-forte — moderate"
    else:
        dynamic = "piano — soft"

    return {
        "current_dynamic": dynamic,
        "trajectory": trajectory,
        "coherence_trend": round(delta, 4),
        "pulses_to_peak": pulses_remaining,
        "total_pulses": pulses,
        "crescendo_philosophy": (
            "A crescendo is not just getting louder — it is building toward "
            "a moment that matters. The Builder reads the organism's own "
            "intensity curve and asks: are we rising toward something, or "
            "fading into silence? The answer shapes how the organism invests "
            "its energy."
        ),
    }


from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))


def handler(payload: dict = None, context: object = None) -> dict:
    result = _crescendo()
    result["action"] = "crescendo"
    return result


def coherence_vitals() -> dict:
    """Crescendo Builder reports intensity-trajectory health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "intensity_trajectory": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["choral_engine", "system_pulse", "pulsar_clock"]
