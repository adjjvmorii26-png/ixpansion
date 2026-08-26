"""Module Analytics — tracks usage patterns, performance, and health across all modules.

The analytics system monitors which modules are used most, how fast they
respond, where errors occur, and which modules are most interconnected.
This data drives optimization decisions and reveals hidden dependencies.
"""
from __future__ import annotations

import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class ModuleMetrics:
    def __init__(self, name: str):
        self.name = name
        self.call_count = 0
        self.total_time = 0.0
        self.error_count = 0
        self.last_called = 0.0
        self.action_counts: Dict[str, int] = {}

    def record_call(self, action: str, elapsed: float, success: bool):
        self.call_count += 1
        self.total_time += elapsed
        self.last_called = time.time()
        self.action_counts[action] = self.action_counts.get(action, 0) + 1
        if not success:
            self.error_count += 1

    @property
    def avg_response_time(self) -> float:
        return self.total_time / max(self.call_count, 1)

    @property
    def error_rate(self) -> float:
        return self.error_count / max(self.call_count, 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "calls": self.call_count,
            "avg_time_ms": round(self.avg_response_time * 1000, 2),
            "errors": self.error_count,
            "error_rate": round(self.error_rate, 4),
            "top_actions": sorted(self.action_counts.items(), key=lambda x: -x[1])[:5],
        }


class ModuleAnalytics:
    def __init__(self):
        self.metrics: Dict[str, ModuleMetrics] = {}
        self.session_start = time.time()

    def record(self, module: str, action: str, elapsed: float, success: bool = True):
        if module not in self.metrics:
            self.metrics[module] = ModuleMetrics(module)
        self.metrics[module].record_call(action, elapsed, success)

    def module_report(self, module: str) -> Dict[str, Any]:
        if module not in self.metrics:
            return {"error": "no data for module"}
        return self.metrics[module].to_dict()

    def top_modules(self, by: str = "calls", top_k: int = 10) -> List[Dict[str, Any]]:
        key_map = {"calls": lambda m: m.call_count, "time": lambda m: m.avg_response_time, "errors": lambda m: m.error_count}
        key_fn = key_map.get(by, key_map["calls"])
        sorted_modules = sorted(self.metrics.values(), key=key_fn, reverse=True)
        return [m.to_dict() for m in sorted_modules[:top_k]]

    def system_health(self) -> Dict[str, Any]:
        if not self.metrics:
            return {"status": "no_data"}
        total_calls = sum(m.call_count for m in self.metrics.values())
        total_errors = sum(m.error_count for m in self.metrics.values())
        avg_time = sum(m.total_time for m in self.metrics.values()) / max(total_calls, 1)
        unhealthy = [m.name for m in self.metrics.values() if m.error_rate > 0.1]
        return {
            "total_modules_tracked": len(self.metrics),
            "total_calls": total_calls,
            "total_errors": total_errors,
            "overall_error_rate": round(total_errors / max(total_calls, 1), 4),
            "avg_response_ms": round(avg_time * 1000, 2),
            "unhealthy_modules": unhealthy,
            "uptime_seconds": round(time.time() - self.session_start, 1),
        }


_analytics = ModuleAnalytics()


def module_analytics_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "record":
        _analytics.record(
            payload.get("module", ""),
            payload.get("action", ""),
            payload.get("elapsed", 0.0),
            payload.get("success", True),
        )
        return {"recorded": True}
    elif action == "module":
        return _analytics.module_report(payload.get("module", ""))
    elif action == "top":
        return {"modules": _analytics.top_modules(payload.get("by", "calls"), payload.get("top_k", 10))}
    return {"status": "active", **_analytics.system_health()}
