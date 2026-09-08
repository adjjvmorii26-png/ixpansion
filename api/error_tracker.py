"""Wave 516: Error Tracker — aggregate and surface module errors across the organism."""
from __future__ import annotations
import json, os, time
from typing import Any, Dict, List

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    errors = []
    # Scan data files for error entries
    if os.path.isdir(DATA_DIR):
        for fname in sorted(os.listdir(DATA_DIR)):
            if fname.endswith(".json") and ("error" in fname or "fail" in fname or "anomal" in fname):
                try:
                    with open(os.path.join(DATA_DIR, fname)) as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        for e in data[-20:]:
                            e["source_file"] = fname
                            errors.append(e)
                    elif isinstance(data, dict):
                        for key in ("entries", "errors", "logs"):
                            for e in data.get(key, [])[-10:]:
                                e["source_file"] = fname
                                errors.append(e)
                except Exception:
                    pass
    # Deduplicate by message
    seen = set()
    unique = []
    for e in errors:
        msg = e.get("error", e.get("message", str(e)))[:100]
        if msg not in seen:
            seen.add(msg)
            unique.append(e)
    unique.sort(key=lambda e: e.get("timestamp", e.get("time", 0)), reverse=True)
    return {
        "action": "error_log",
        "total": len(unique),
        "errors": unique[:50],
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
