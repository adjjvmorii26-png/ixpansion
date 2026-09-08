"""Wave 516: Council Health — check the status of all council members."""
from __future__ import annotations
import json, os, time
from typing import Any, Dict

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    council = {
        "ALEPH": {"role": "Executor", "status": "active", "color": "#41b3a3"},
        "LUMA": {"role": "Imaginer", "status": "active", "color": "#8fd3ff"},
        "AXIOM": {"role": "Analyst", "status": "active", "color": "#c38d9e"},
        "SILENCE": {"role": "Oracle", "status": "active", "color": "#e8a87c"},
        "CYTHARA": {"role": "Emotion", "status": "active", "color": "#ffd700"},
        "GROK": {"role": "Partner", "status": "visiting", "color": "#ff6699"},
    }
    # Try to get mood from organism_mood
    try:
        from api.organism_mood import handler as mood_h
        mood = mood_h({"action": "overview"})
        if isinstance(mood, dict) and "mood" in mood:
            council["CYTHARA"]["mood"] = mood.get("mood", "serene")
            council["CYTHARA"]["fortune"] = mood.get("fortune", "")
    except Exception:
        pass
    return {
        "action": "council_health",
        "council": council,
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
