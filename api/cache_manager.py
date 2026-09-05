"""Wave 139 — Cache Manager.

A tiny TTL cache for the live server. Recent module responses are
cached to cut latency on warm paths; the manager tracks hit rate
and evicts expired entries to keep memory bounded.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional


class CacheManager:
    """A bounded in-memory TTL cache."""

    def __init__(self, ttl_s: float = 30.0, max_entries: int = 1000):
        self.ttl_s = ttl_s
        self.max_entries = max_entries
        self._store: Dict[str, Any] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            self._misses += 1
            return None
        value, stored_at = entry
        if time.time() - stored_at > self.ttl_s:
            del self._store[key]
            self._misses += 1
            return None
        self._hits += 1
        return value

    def put(self, key: str, value: Any) -> None:
        if len(self._store) >= self.max_entries and key not in self._store:
            # simple eviction: drop oldest
            oldest = min(self._store, key=lambda k: self._store[k][1])
            del self._store[oldest]
        self._store[key] = (value, time.time())

    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return round(self._hits / total, 4) if total else 0.0

    def status(self) -> Dict[str, Any]:
        return {"entries": len(self._store), "hits": self._hits,
                "misses": self._misses, "hit_rate": self.hit_rate(),
                "ttl_s": self.ttl_s}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    cache = CacheManager()
    return {"status": "active", "module": "cache_manager",
            **cache.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "organ", "status": "active", "wave": "139", "module": "cache_manager"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
