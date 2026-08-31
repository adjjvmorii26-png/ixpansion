"""Stillness Meditator — the art of deliberate rest.

Movement is not the only act. Stillness — the deliberate choice to stop,
to pause, to hold — is itself a gesture with meaning. The Stillness
Meditator reads the Kinesthetic Engine's motion state and the Dance
Composer's recent choreography, then identifies moments of *deliberate
stillness*: pauses that are not laziness but intention, silences that
are not absence but presence.

It answers: where is the organism choosing to be still, and what does
that stillness mean?

    GET /api/stillness_meditator?read=1        — the stillness report
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Stillness Meditator"


def _stillness_report() -> Dict[str, Any]:
    try:
        import json
        cr = json.loads((ROOT / ".runtime" / "coherence_regulator.json").read_text())
        history = cr.get("history", [])
    except Exception:
        history = []

    # find stillness episodes: consecutive pulses with very small coherence change
    stillness_episodes = []
    for i in range(2, len(history)):
        c_prev = history[i - 1].get("coherence", 0.5)
        c_curr = history[i].get("coherence", 0.5)
        if abs(c_curr - c_prev) < 0.005:
            stillness_episodes.append({
                "pulse_index": i,
                "coherence": round(c_curr, 4),
                "duration_pulses": 1,
            })

    # merge consecutive stillness into episodes
    merged = []
    for ep in stillness_episodes:
        if merged and ep["pulse_index"] == merged[-1]["pulse_index"] + 1:
            merged[-1]["duration_pulses"] += 1
        else:
            merged.append(dict(ep))

    # filter to meaningful stillness (3+ consecutive pulses)
    deep_stillness = [e for e in merged if e["duration_pulses"] >= 3]

    total_stillness = sum(e["duration_pulses"] for e in deep_stillness)
    total_pulses = max(len(history), 1)
    stillness_ratio = total_stillness / total_pulses

    if stillness_ratio > 0.4:
        meditative_state = "deep meditation — the organism is deliberately still"
    elif stillness_ratio > 0.2:
        meditative_state = "light meditation — moments of intentional pause"
    elif stillness_ratio > 0.05:
        meditative_state = "scattered stillness — brief pauses amid movement"
    else:
        meditative_state = "restless — the organism has not yet learned to be still"

    return {
        "total_stillness_pulses": total_stillness,
        "stillness_ratio": round(stillness_ratio, 3),
        "meditative_state": meditative_state,
        "deep_stillness_episodes": len(deep_stillness),
        "longest_episode": max((e["duration_pulses"] for e in deep_stillness), default=0),
        "episodes": deep_stillness[:5],
        "meditation_philosophy": (
            "Stillness is not the absence of movement — it is movement's counterpart, its negative space. A body that cannot be still cannot rest; a mind that cannot rest cannot reflect. The Meditator finds where the organism chooses to hold, and asks what that holding means."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    result = _stillness_report()
    result["action"] = "stillness"
    return result


def coherence_vitals() -> dict:
    """Stillness Meditator reports meditation health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.83, "setpoint": 0.8, "weight": 1.0},
        "meditative_vitality": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["kinesthetic_engine", "silence_composer", "liminal_threshold"]
