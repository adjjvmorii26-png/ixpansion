"""Wave 516: Visitor Map — geographies of visitors from the visitor log."""
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
    path = os.path.join(DATA_DIR, "visitor_log.json")
    visitors = []
    try:
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            if isinstance(data, dict):
                visitors = data.get("visits", data.get("visitors", []))
            elif isinstance(data, list):
                visitors = data
    except Exception:
        pass
    total = len(visitors)
    unique_ip = len(set(v.get("ip") or v.get("visitor_id") or "" for v in visitors if v.get("ip") or v.get("visitor_id")))
    recent = [v for v in visitors if (v.get("timestamp") or v.get("time") or 0) > time.time() - 86400]
    return {
        "action": "visitor_map",
        "total_visitors": total,
        "unique_ips": unique_ip,
        "visitors_last_24h": len(recent),
        "visitors": visitors[-20:],
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
