"""Response Cache — caches API responses with TTL and invalidation.

Reduces latency by caching frequently requested responses.
Supports manual invalidation and automatic TTL expiration.
"""
from __future__ import annotations

import hashlib
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class ResponseCache:
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict] = {}
        self.stats = {"hits": 0, "misses": 0, "sets": 0, "invalidations": 0}

    def set(self, key: str, value: Any, ttl: int = None) -> Dict:
        self.cache[key] = {"value": value, "created": time.time(), "ttl": ttl or self.default_ttl}
        self.stats["sets"] += 1
        return {"cached": True, "key": key}

    def get(self, key: str) -> Dict:
        if key not in self.cache:
            self.stats["misses"] += 1
            return {"hit": False}
        entry = self.cache[key]
        if time.time() - entry["created"] > entry["ttl"]:
            del self.cache[key]
            self.stats["misses"] += 1
            return {"hit": False, "reason": "expired"}
        self.stats["hits"] += 1
        return {"hit": True, "value": entry["value"]}

    def invalidate(self, key: str) -> Dict:
        if key in self.cache:
            del self.cache[key]
            self.stats["invalidations"] += 1
            return {"invalidated": True}
        return {"invalidated": False, "reason": "not found"}

    def clear(self) -> Dict:
        count = len(self.cache)
        self.cache.clear()
        return {"cleared": count}

    def get_stats(self) -> Dict:
        return {**self.stats, "entries": len(self.cache)}


def handler(request, response):
    c = ResponseCache()
    return c.get_stats()


def demo():
    c = ResponseCache()
    print("=== Response Cache ===")
    c.set("key1", {"data": "value1"})
    r1 = c.get("key1")
    print(f"\n  Hit: {r1['hit']}, value: {r1.get('value')}")
    r2 = c.get("key2")
    print(f"  Miss: {not r2['hit']}")
    c.invalidate("key1")
    r3 = c.get("key1")
    print(f"  After invalidate: {r3['hit']}")
    print(f"  Stats: {c.get_stats()}")
    return c.get_stats()


if __name__ == "__main__":
    demo()

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "0", "module": "response_cache"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
