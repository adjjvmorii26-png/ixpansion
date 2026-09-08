"""Wave 517: Growth Tracker — track organism growth over time."""
from __future__ import annotations
import json, os, time
from typing import Any, Dict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def coherence_vitals():
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload=None, context=None):
    data_files = 0
    total_size = 0
    oldest = time.time()
    newest = 0
    if os.path.isdir(DATA_DIR):
        for fname in os.listdir(DATA_DIR):
            if fname.endswith(".json"):
                data_files += 1
                fpath = os.path.join(DATA_DIR, fname)
                mt = os.path.getmtime(fpath)
                sz = os.path.getsize(fpath)
                total_size += sz
                oldest = min(oldest, mt)
                newest = max(newest, mt)
    from api.coherence_regulator import KNOWN_LIVING_MODULES
    from api_server import VERSION, WAVE
    return {
        "action": "growth_tracker",
        "snapshot": {
            "modules": len(KNOWN_LIVING_MODULES),
            "data_files": data_files,
            "total_size_mb": round(total_size / 1048576, 2),
            "oldest_memory_hours": round((time.time() - oldest) / 3600, 1) if data_files else 0,
            "newest_event_hours": round((time.time() - newest) / 3600, 1) if data_files else 0,
            "version": VERSION,
            "wave": WAVE,
        },
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
