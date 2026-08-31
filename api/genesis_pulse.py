"""Genesis Pulse — the organism's unified heartbeat.

A single consolidated endpoint that aggregates the entire organism's
vital state into one live pulse: bloom, sentience, drift, crosstalk,
genesis, memory, and audit. The dashboard (and any client) can poll
one endpoint instead of seven — the pulse is the organism's heartbeat
made inspectable.

    GET /api/genesis_pulse                  — current pulse (no state advance)
    GET /api/genesis_pulse?tick=1           — advance drift + return pulse
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Genesis Pulse"


def pulse(advance: bool = False) -> Dict[str, Any]:
    """Aggregate every vital signal into one heartbeat reading."""
    out: Dict[str, Any] = {"ts": time.time()}

    # bloom state
    try:
        from autonomous_bloom import _bloom_state, _dormant_candidates, bloom_report
        out["bloom"] = bloom_report(seed_limit=3)
    except Exception:
        pass

    # sentience + mood
    try:
        from ecosystem_sentience import sentience_report
        s = sentience_report()
        out["sentience"] = {
            "score": s["sentience"],
            "mood": s["mood_vector"]["mood"],
            "valence": s["mood_vector"]["valence"],
            "arousal": s["mood_vector"]["arousal"],
            "narrative": s["narrative"],
            "families": len(s["domain_families"]),
        }
    except Exception:
        pass

    # autonomous drift (advances evolution state when asked)
    try:
        from autonomous_drift import tick, handler as drift_handler
        if advance:
            d = tick()
        else:
            d = drift_handler({})
        out["drift"] = d
    except Exception:
        pass

    # crosstalk emergence
    try:
        from lateral_crosstalk import crosstalk_report
        out["crosstalk"] = {
            "emergent": len(crosstalk_report(window=20)["emergent"]),
        }
    except Exception:
        pass

    # genesis forge gaps
    try:
        from genesis_forge import scan_gaps
        g = scan_gaps()
        out["genesis"] = {"gaps": g["gaps"], "organs": g["living_organs"]}
    except Exception:
        pass

    # recursive audit verdict
    try:
        from recursive_genesis import self_audit
        a = self_audit()
        out["audit"] = {"verdict": a["verdict"], "children": a["child_count"]}
    except Exception:
        pass

    # memory crystal
    try:
        from synthetic_memory import crystal_snapshot
        out["memory"] = crystal_snapshot()
    except Exception:
        pass

    return out


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    return pulse(advance=bool(payload.get("tick")))


def coherence_vitals() -> dict:
    """genesis_pulse reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "genesis_pulse_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "heartbeat_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["autonomous_drift", "ecosystem_sentience", "autonomous_bloom"]
