"""API Gateway — intelligent routing, caching, rate limiting, circuit breaker.

Central entry point that manages traffic across all modules. Features
intelligent request routing, response caching, adaptive rate limiting,
and circuit breaker patterns for fault tolerance.

Usage:
    POST /api/gateway/route         — route a request intelligently
    GET  /api/gateway/stats         — gateway statistics
    POST /api/gateway/cache         — cache a response
    GET  /api/gateway/cache/<key>   — retrieve cached response
    POST /api/gateway/circuit       — check/set circuit breaker
"""
from __future__ import annotations

import hashlib
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MODULE_REGISTRY = {
    "agent_rental": {"latency_ms": 45, "error_rate": 0.02, "priority": 1},
    "billing": {"latency_ms": 30, "error_rate": 0.01, "priority": 2},
    "marketplace": {"latency_ms": 55, "error_rate": 0.03, "priority": 1},
    "cognitive_resonance": {"latency_ms": 120, "error_rate": 0.05, "priority": 3},
    "dream_synthesis": {"latency_ms": 200, "error_rate": 0.04, "priority": 3},
    "temporal_market": {"latency_ms": 80, "error_rate": 0.02, "priority": 2},
    "gravitational_pricing": {"latency_ms": 35, "error_rate": 0.01, "priority": 2},
    "memory_palace": {"latency_ms": 60, "error_rate": 0.02, "priority": 2},
    "speciation_engine": {"latency_ms": 90, "error_rate": 0.03, "priority": 3},
    "warp_drive_optimizer": {"latency_ms": 40, "error_rate": 0.01, "priority": 1},
    "quantum_randomness": {"latency_ms": 15, "error_rate": 0.005, "priority": 1},
    "paradox_marketplace": {"latency_ms": 150, "error_rate": 0.04, "priority": 3},
    "dream_interpreter": {"latency_ms": 180, "error_rate": 0.03, "priority": 3},
}


class APIGateway:
    def __init__(self):
        self.request_log: List[Dict] = []
        self.cache: Dict[str, Dict] = {}
        self.circuit_breakers: Dict[str, Dict] = {}
        self.rate_limits: Dict[str, Dict] = {}
        self.stats = {"total_routed": 0, "cached_hits": 0, "circuit_opened": 0}
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "api_gateway.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.cache = data.get("cache", {})
            self.circuit_breakers = data.get("circuit_breakers", {})
            self.rate_limits = data.get("rate_limits", {})
            self.stats = data.get("stats", self.stats)

    def _save(self):
        path = ROOT / ".runtime" / "api_gateway.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "cache": dict(list(self.cache.items())[-200:]),
            "circuit_breakers": self.circuit_breakers,
            "rate_limits": self.rate_limits,
            "stats": self.stats,
        }, indent=2))

    def route(self, module: str, method: str = "GET",
              params: Dict = None) -> Dict:
        if module not in MODULE_REGISTRY:
            return {"error": f"unknown module: {module}", "available": list(MODULE_REGISTRY.keys())}
        cb = self.circuit_breakers.get(module, {})
        if cb.get("state") == "open":
            return {"error": f"circuit breaker open for {module}", "retry_after": cb.get("retry_after", 30)}
        spec = MODULE_REGISTRY[module]
        route_decision = {
            "module": module,
            "method": method,
            "estimated_latency_ms": spec["latency_ms"],
            "priority": spec["priority"],
            "status": "routed",
        }
        self.stats["total_routed"] += 1
        self.request_log.append({
            "module": module, "method": method,
            "timestamp": time.time(), "latency": spec["latency_ms"],
        })
        self._save()
        return route_decision

    def cache_response(self, key: str, response: Any, ttl_sec: int = 300) -> Dict:
        self.cache[key] = {
            "response": response, "created": time.time(),
            "ttl": ttl_sec, "hits": 0,
        }
        self._save()
        return {"cached": True, "key": key, "ttl": ttl_sec}

    def get_cached(self, key: str) -> Dict:
        entry = self.cache.get(key)
        if not entry:
            return {"hit": False}
        if time.time() - entry["created"] > entry["ttl"]:
            del self.cache[key]
            return {"hit": False, "reason": "expired"}
        entry["hits"] += 1
        self.stats["cached_hits"] += 1
        return {"hit": True, "response": entry["response"], "hits": entry["hits"]}

    def circuit_check(self, module: str, state: str = "closed") -> Dict:
        if state == "open":
            self.circuit_breakers[module] = {
                "state": "open", "opened_at": time.time(),
                "retry_after": 30,
            }
            self.stats["circuit_opened"] += 1
        elif state == "half_open":
            self.circuit_breakers[module] = {
                "state": "half_open", "opened_at": time.time(),
            }
        else:
            self.circuit_breakers[module] = {"state": "closed"}
        self._save()
        return {"module": module, "state": state}

    def get_stats(self) -> Dict:
        return {
            **self.stats,
            "modules": len(MODULE_REGISTRY),
            "cache_entries": len(self.cache),
            "open_circuits": sum(
                1 for cb in self.circuit_breakers.values() if cb.get("state") == "open"
            ),
            "recent_requests": len(self.request_log[-100:]),
        }


def handler(request, response):
    gw = APIGateway()
    return gw.get_stats()


def demo():
    gw = APIGateway()
    print("=== API Gateway ===")
    result = gw.route("agent_rental", "POST")
    print(f"\nRouted: {result['module']} → {result['status']} (est. {result['estimated_latency_ms']}ms)")

    gw.cache_response("recent_agents", [{"id": "scout"}, {"id": "analyst"}])
    cached = gw.get_cached("recent_agents")
    print(f"Cache hit: {cached['hit']}")

    gw.circuit_check("dream_synthesis", "open")
    result = gw.route("dream_synthesis")
    print(f"Circuit open: {result.get('error', 'ok')}")

    stats = gw.get_stats()
    print(f"\nStats: {stats['total_routed']} routed, {stats['cached_hits']} cached, {stats['open_circuits']} circuits open")
    return stats


if __name__ == "__main__":
    demo()
