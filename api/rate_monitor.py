"""Wave 516: Rate Monitor — track request rates and throttling status."""
from __future__ import annotations
import time
from typing import Any, Dict

_request_log: list = []

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    now = time.time()
    # Prune old entries (last 60s)
    global _request_log
    _request_log = [t for t in _request_log if now - t < 60]
    _request_log.append(now)
    rate_1m = len(_request_log)
    rate_10s = len([t for t in _request_log if now - t < 10])
    threshold = 60  # per minute
    return {
        "action": "rate_monitor",
        "rate_1m": rate_1m,
        "rate_10s": rate_10s,
        "threshold_per_min": threshold,
        "throttled": rate_1m > threshold,
        "time": now,
        "vitals": coherence_vitals(),
    }
