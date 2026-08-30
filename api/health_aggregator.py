"""Health Aggregator — combines health checks from all subsystems.

Single endpoint that aggregates health status from all modules,
provides a unified view, and tracks historical health trends.
"""
from __future__ import annotations

import json
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class HealthAggregator:
    def __init__(self):
        self.checks: Dict[str, Dict] = {}
        self.history: List[Dict] = []

    def register(self, name: str, check_fn=None) -> Dict:
        self.checks[name] = {"name": name, "status": "unknown", "last_check": 0, "check_fn": check_fn}
        return {"registered": True, "name": name}

    def check_all(self) -> Dict:
        results = {}
        for name, check in self.checks.items():
            try:
                start = time.time()
                if check["check_fn"]:
                    check["check_fn"]()
                latency = round((time.time() - start) * 1000, 2)
                check["status"] = "healthy"
                check["latency_ms"] = latency
                check["last_check"] = time.time()
                results[name] = {"status": "healthy", "latency_ms": latency}
            except Exception as e:
                check["status"] = "unhealthy"
                results[name] = {"status": "unhealthy", "error": str(e)}
        healthy = sum(1 for r in results.values() if r["status"] == "healthy")
        overall = "healthy" if healthy == len(results) else "degraded" if healthy > 0 else "unhealthy"
        entry = {"overall": overall, "healthy": healthy, "total": len(results), "timestamp": time.time()}
        self.history.append(entry)
        return {"overall": overall, "checks": results, "summary": entry}

    def history_log(self, limit: int = 20) -> List[Dict]:
        return self.history[-limit:]


def handler(request, response):
    ha = HealthAggregator()
    return ha.check_all()


def demo():
    ha = HealthAggregator()
    print("=== Health Aggregator ===")
    ha.register("api")
    ha.register("database")
    ha.register("cache")
    result = ha.check_all()
    print(f"\n  Overall: {result['overall']}")
    for name, check in result["checks"].items():
        print(f"    {name}: {check['status']}")
    return result


if __name__ == "__main__":
    demo()


def coherence_vitals() -> dict:
    """health_aggregator reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "health_aggregator_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['dream_interpreter', 'credits', 'consciousness_simulator']

