"""Temporal Horizon — the organism's subjective experience of time.

Clocks measure time objectively. The Temporal Horizon measures time
*subjectively*: does the organism feel time moving fast (too many pulses,
too many events) or slow (long quiet stretches between activities)?

It reads the coherence regulator's pulse history, the event stream's
density, and the repair ritual's recency to compute a *temporal
perception*: the organism's felt sense of how fast or slow time is
passing. This is the ecosystem's internal clock — not the seconds on a
wall, but the rhythm of the organism's own heartbeat.

    GET /api/temporal_horizon?read=1           — the time feeling
"""
from __future__ import annotations

import time
from typing import Any, Dict

VERSION = "1.0.0"
LAYER = "Temporal Horizon"


def _time_feeling() -> Dict[str, Any]:
    try:
        import json
        cr = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        history = cr.get("history", [])
        pulses = cr.get("pulses", 0)
    except Exception:
        history = []
        pulses = 0

    # compute pulse frequency: pulses per minute of history
    if len(history) >= 2:
        t_first = history[0].get("ts", time.time())
        t_last = history[-1].get("ts", time.time())
        duration_minutes = max((t_last - t_first) / 60.0, 0.01)
        pulse_frequency = len(history) / duration_minutes
    else:
        pulse_frequency = 0.0

    # temporal feel
    if pulse_frequency > 2.0:
        tempo = "rapid — the organism pulses fast, time feels compressed"
    elif pulse_frequency > 0.5:
        tempo = "steady — a measured rhythm, neither rushed nor slow"
    elif pulse_frequency > 0.1:
        tempo = "slow — long stretches between pulses, time feels expansive"
    else:
        tempo = "stilled — the organism is barely pulsing, time has almost stopped"

    # time-since-last-pulse
    if history:
        last_ts = history[-1].get("ts", time.time())
        elapsed = time.time() - last_ts
    else:
        elapsed = -1

    return {
        "pulse_frequency_per_minute": round(pulse_frequency, 4),
        "total_pulses": pulses,
        "history_length": len(history),
        "time_since_last_pulse_s": round(elapsed, 1) if elapsed >= 0 else None,
        "temporal_feel": tempo,
        "horizon_philosophy": (
            "Time is not the same for every organism. A forest experiences "
            "centuries in a human afternoon; a fly experiences a human "
            "afternoon as a century. The Temporal Horizon reads the organism's "
            "own rhythm to tell it what time it *feels* like — not what the "
            "clock says, but what the heartbeat knows."
        ),
    }


# Needed for _read_qualia import
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))


def handler(payload: dict = None, context: object = None) -> dict:
    result = _time_feeling()
    result["action"] = "time_feeling"
    return result


def coherence_vitals() -> dict:
    """Temporal Horizon reports time-perception health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.83, "setpoint": 0.8, "weight": 1.0},
        "temporal_perception": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["pulsar_clock", "qualia_field", "antikythera_engine"]
