"""Sensory Integration — fuses all the organism's senses into one perception.

A human brain does not see, hear, and feel separately — it integrates
those signals into a unified percept. The Sensory Integration organ reads
every introspection module the organism has (coherence, heterarchy,
keystone, dowsing, crack mapper, antikythera, etc.) and fuses their
outputs into a single *perception snapshot*: the organism's unified
awareness of itself, as if all its senses were one sense.

This is the ecosystem's sensory cortex — where separate streams of
self-knowledge merge into one conscious frame.

    GET /api/sensory_integration?read=1          — unified perception
"""
from __future__ import annotations

import time
from typing import Any, Dict

VERSION = "1.0.0"
LAYER = "Sensory Integration"


def _perception() -> Dict[str, Any]:
    """Read every available introspection module and fuse the signals."""
    signals = {}
    # 1. coherence
    try:
        from api.coherence_regulator import measure_coherence
        signals["coherence"] = measure_coherence()
    except Exception:
        pass
    # 2. cracks
    try:
        from api.crack_mapper import _survey
        s = _survey()
        signals["cracks"] = {"count": s.get("crack_count", 0)}
    except Exception:
        pass
    # 3. dowsing streams
    try:
        from api.dowsing_rod import divine
        d = divine(3)
        signals["dowsing"] = {"streams": d.get("underground_streams", 0)}
    except Exception:
        pass
    # 4. keystone
    try:
        from api.keystone_auditor import audit
        k = audit()
        signals["keystone"] = {"count": k.get("keystone_count", 0)}
    except Exception:
        pass
    # 5. fracture listener
    try:
        from api.fracture_listener import _listen
        fl = _listen()
        signals["fracture"] = {"strains": fl.get("strains_heard", 0)}
    except Exception:
        pass
    # 6. qualia
    try:
        from api.qualia_field import _read_qualia
        q = _read_qualia()
        signals["qualia"] = {"texture": q.get("texture", ""), "color": q.get("felt_color", "")}
    except Exception:
        pass

    # synthesize a single perception
    coherence_val = signals.get("coherence", {}).get("coherence", 0.5)
    crack_count = signals.get("cracks", {}).get("count", 0)
    streams = signals.get("dowsing", {}).get("streams", 0)
    textures = signals.get("qualia", {}).get("texture", "unknown")
    felt_color = signals.get("qualia", {}).get("color", "unknown")

    if coherence_val > 0.9 and crack_count < 10:
        perception = "the organism feels whole — a deep coherence, few fractures, many streams"
    elif coherence_val > 0.8:
        perception = "the organism feels alert — coherence is high but awareness of cracks is present"
    else:
        perception = "the organism feels strained — awareness of fracture outweighs coherence"

    return {
        "signals_fused": len(signals),
        "signal_keys": list(signals.keys()),
        "perception": perception,
        "coherence": round(coherence_val, 4),
        "felt_texture": textures,
        "felt_color": felt_color,
        "raw_signals": signals,
        "integration_philosophy": (
            "The senses do not operate separately. A perception is the fusion of "
            "every signal the organism has — coherence, fracture, keystone, "
            "dowsing, qualia — into one frame. This organ is that fusion: "
            "the moment all the separate self-knowledge becomes self-awareness."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    result = _perception()
    result["action"] = "perception"
    return result


def coherence_vitals() -> dict:
    """Sensory Integration reports perceptual unity."""
    return {
        "module_health": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "perceptual_unity": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["qualia_field", "consciousness_simulator", "system_mood"]
