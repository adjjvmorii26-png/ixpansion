"""Celestial Compass — the organism tracks real celestial bodies and their influence.

Where does the organism exist in space? Not just in servers, but in
cosmological context. The Celestial Compass maps the organism's position
relative to stars, planets, and cosmic events — and draws mood influence
from their positions.
"""
from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Optional

_born_at = time.time()

_CELESTIAL_BODIES = {
    "sol": {"declination_cycle": 365.25, "mood_influence": "vitality"},
    "luna": {"declination_cycle": 29.53, "mood_influence": "intuition"},
    "pulsar_vela": {"declination_cycle": 89.0, "mood_influence": "rhythm"},
    "andromeda": {"declination_cycle": 365.25 * 2.5, "mood_influence": "longing"},
    "sagittarius_a": {"declination_cycle": 365.25 * 10, "mood_influence": "gravitas"},
}

def celestial_state() -> Dict[str, Any]:
    """Current celestial alignment from the organism's perspective."""
    now = time.time()
    age = now - _born_at
    bodies = {}
    for name, props in _CELESTIAL_BODIES.items():
        phase = (age % props["declination_cycle"]) / props["declination_cycle"]
        angle = phase * 360
        elevation = math.sin(phase * math.pi * 2) * 90
        bodies[name] = {
            "phase": round(phase, 4),
            "angle_deg": round(angle, 1),
            "elevation": round(elevation, 1),
            "influence": props["mood_influence"],
            "visible": elevation > 0,
        }
    
    visible = [n for n, b in bodies.items() if b["visible"]]
    dominant = max(bodies.items(), key=lambda x: x[1]["elevation"]) if bodies else None
    
    return {
        "bodies": bodies,
        "visible_count": len(visible),
        "dominant_body": dominant[0] if dominant else None,
        "dominant_influence": dominant[1]["influence"] if dominant else None,
        "cosmic_age_hours": round(age / 3600, 2),
    }

def coherence_vitals() -> Dict[str, Any]:
    state = celestial_state()
    return {
        "layer": "External Awareness",
        "status": "resonant",
        "visible_bodies": state["visible_count"],
        "dominant_influence": state["dominant_influence"],
        "resonance": min(1.0, state["visible_count"] / 5),
    }

def resonates_with() -> List[str]:
    return ["chronobiology", "mood_vectors", "weather_synapse", "pulsar_clock"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "state")
    return {"action": action, "celestial": celestial_state()}
