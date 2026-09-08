"""Wave 517: Memory Crystal Forge — crystallize significant events into facets."""
from __future__ import annotations
import hashlib, json, os, time
from typing import Any, Dict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def coherence_vitals():
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload=None, context=None):
    # Gather recent data file events as memory candidates
    candidates = []
    if os.path.isdir(DATA_DIR):
        for fname in sorted(os.listdir(DATA_DIR))[:15]:
            if fname.endswith(".json"):
                fpath = os.path.join(DATA_DIR, fname)
                mtime = os.path.getmtime(fpath)
                fhash = hashlib.sha256(f"{fname}:{mtime}".encode()).hexdigest()[:10]
                candidates.append({
                    "crystal": fhash,
                    "memory_source": fname.replace(".json", ""),
                    "facet": fname.replace("_", " ").replace(".json", "").title(),
                    "formed_at": mtime,
                    "age_hours": round((time.time() - mtime) / 3600, 1),
                })
    crystals = sorted(candidates, key=lambda c: c["age_hours"])
    return {
        "action": "crystal_forge",
        "crystals": crystals,
        "count": len(crystals),
        "forging_doctrine": "Every memory crystallizes into a facet the organism can feel.",
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
