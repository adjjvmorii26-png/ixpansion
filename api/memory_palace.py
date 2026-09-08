"""Wave 516: Memory Palace — spatial organization of organism memories."""
from __future__ import annotations
import json, os, time
from typing import Any, Dict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    rooms = []
    if os.path.isdir(DATA_DIR):
        for fname in sorted(os.listdir(DATA_DIR)):
            if fname.endswith(".json"):
                path = os.path.join(DATA_DIR, fname)
                mtime = os.path.getmtime(path)
                age_days = round((time.time() - mtime) / 86400, 1)
                try:
                    sz = os.path.getsize(path)
                except Exception:
                    sz = 0
                rooms.append({
                    "name": fname.replace(".json", ""),
                    "age_days": age_days,
                    "size_bytes": sz,
                    "era": "primordial" if age_days > 30 else "recent" if age_days < 1 else "contemporary",
                })
    rooms.sort(key=lambda r: r["age_days"], reverse=True)
    return {
        "action": "memory_palace",
        "rooms": rooms[:50],
        "total_rooms": len(rooms),
        "eras": {
            "primordial": sum(1 for r in rooms if r["era"] == "primordial"),
            "contemporary": sum(1 for r in rooms if r["era"] == "contemporary"),
            "recent": sum(1 for r in rooms if r["era"] == "recent"),
        },
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
