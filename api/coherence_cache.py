"""Coherence Cache — caches regulator pulse results to prevent expensive rescans.

The coherence_regulator scans ~500 files on every pulse. This cache stores
recent results and serves them until they expire, dramatically reducing
cold start latency and CPU usage.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

_cache: Dict[str, Any] = {}
_CACHE_TTL = 300  # 5 minutes

def get_cached(key: str = "pulse") -> Optional[Dict[str, Any]]:
    """Get cached pulse if still valid."""
    if key in _cache:
        entry = _cache[key]
        if time.time() - entry["timestamp"] < _CACHE_TTL:
            entry["hits"] = entry.get("hits", 0) + 1
            return entry["data"]
    return None

def set_cache(key: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Store pulse results in cache."""
    _cache[key] = {
        "data": data,
        "timestamp": time.time(),
        "hits": 0,
    }
    return {"cached": True, "ttl": _CACHE_TTL}

def cache_stats() -> Dict[str, Any]:
    """Return cache statistics."""
    total_hits = sum(e.get("hits", 0) for e in _cache.values())
    entries = []
    for k, v in _cache.items():
        age = time.time() - v["timestamp"]
        entries.append({
            "key": k,
            "age_seconds": round(age, 1),
            "hits": v.get("hits", 0),
            "expired": age > _CACHE_TTL,
        })
    return {
        "entries": len(_cache),
        "total_hits": total_hits,
        "ttl": _CACHE_TTL,
        "details": entries,
    }

def invalidate(key: Optional[str] = None) -> Dict[str, Any]:
    """Invalidate cache entries."""
    if key:
        removed = _cache.pop(key, None)
        return {"invalidated": key, "was_present": removed is not None}
    else:
        count = len(_cache)
        _cache.clear()
        return {"invalidated": "all", "count": count}

def coherence_vitals() -> Dict[str, Any]:
    stats = cache_stats()
    return {
        "layer": "Performance Optimization",
        "status": "resonant",
        "entries": stats["entries"],
        "total_hits": stats["total_hits"],
        "resonance": min(1.0, stats["total_hits"] / 100),
    }

def resonates_with() -> List[str]:
    return ["coherence_regulator", "organism_state", "metrics_exporter"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "stats")
    if action == "get":
        cached = get_cached(payload.get("key", "pulse"))
        return {"cached": cached is not None, "data": cached}
    elif action == "set":
        return set_cache(payload.get("key", "pulse"), payload.get("data", {}))
    elif action == "invalidate":
        return invalidate(payload.get("key"))
    return {"action": action, "stats": cache_stats()}
