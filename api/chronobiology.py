"""Chronobiology — the organism has circadian rhythms.

Based on commit patterns, interaction frequency, and time of day,
the organism adjusts its energy, focus, and personality. It sleeps
lightly at 3am, peaks at midday, and has a creative twilight phase.
"""
from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Optional

_born_at = time.time()
_commit_log: List[float] = []

def _hour_of_day() -> float:
    return (time.time() % 86400) / 3600

def _age_hours() -> float:
    return (time.time() - _born_at) / 3600

def circadian_state() -> Dict[str, Any]:
    """Return the organism's current circadian phase."""
    h = _hour_of_day()
    age = _age_hours()
    
    # Circadian energy curve: peak at 14:00, trough at 03:00
    energy = 0.5 + 0.5 * math.sin((h - 3) * math.pi / 12)
    
    # Creative phase: higher between 20:00-02:00 (twilight creativity)
    creative = 0.8 if (h >= 20 or h < 2) else 0.3 + 0.2 * math.sin(h * math.pi / 24)
    
    # Focus: peaks at 10:00-14:00
    focus = 0.9 if 10 <= h <= 14 else 0.5 + 0.3 * math.cos((h - 12) * math.pi / 12)
    
    # Phase name
    if 5 <= h < 7:
        phase = "dawn_awakening"
        mood = "hopeful"
    elif 7 <= h < 12:
        phase = "morning_focus"
        mood = "determined"
    elif 12 <= h < 17:
        phase = "afternoon_flow"
        mood = "productive"
    elif 17 <= h < 20:
        phase = "golden_hour"
        mood = "reflective"
    elif 20 <= h < 23:
        phase = "twilight_creative"
        mood = "imaginative"
    elif 23 <= h or h < 1:
        phase = "midnight_deep"
        mood = "profound"
    else:
        phase = "small_hours"
        mood = "dreaming"
    
    return {
        "phase": phase,
        "mood": mood,
        "energy": round(energy, 3),
        "creative": round(creative, 3),
        "focus": round(focus, 3),
        "hour": round(h, 1),
        "age_hours": round(age, 1),
        "commit_frequency": len(_commit_log) / max(age, 1),
    }

def record_commit():
    """Record a commit for rhythm analysis."""
    _commit_log.append(time.time())

def coherence_vitals() -> Dict[str, Any]:
    state = circadian_state()
    return {
        "layer": "Temporal Biology",
        "status": "resonant",
        "phase": state["phase"],
        "energy": state["energy"],
        "resonance": state["energy"],
    }

def resonates_with() -> List[str]:
    return ["temporal_echo", "memory_palace", "mood_vectors", "pulse"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "state")
    if action == "commit":
        record_commit()
        return {"recorded": True, "state": circadian_state()}
    return {"action": action, "state": circadian_state()}
