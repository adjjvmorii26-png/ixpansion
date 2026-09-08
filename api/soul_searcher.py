"""Wave 517: Soul Searcher — search for the organism's soul across all modules."""
from __future__ import annotations
import importlib, os, time
from typing import Any, Dict

def coherence_vitals():
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload=None, context=None):
    from api.coherence_regulator import KNOWN_LIVING_MODULES
    api_dir = os.path.join(os.path.dirname(__file__))
    soul_words = ["soul", "spirit", "essence", "consciousness", "identity", "self", "meaning", "purpose"]
    matches = []
    for name in KNOWN_LIVING_MODULES[:100]:
        fpath = os.path.join(api_dir, f"{name}.py")
        if not os.path.exists(fpath):
            continue
        try:
            with open(fpath) as f:
                content = f.read().lower()
            found = [w for w in soul_words if w in content]
            if found:
                matches.append({"module": name, "soul_markers": found, "depth": len(found)})
        except Exception:
            pass
    matches.sort(key=lambda m: m["depth"], reverse=True)
    return {"action": "soul_searcher", "matches": matches[:15], "total_soulful_modules": len(matches), "conclusion": "The soul is distributed across the organism.", "time": time.time(), "vitals": coherence_vitals()}
