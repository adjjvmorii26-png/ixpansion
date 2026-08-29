"""Wave 139 — Metrics Exporter.

Exposes the platform's operational metrics in a machine-readable
format (Prometheus-style text). Aggregates per-module hit counts,
latency averages, and error rates so the live server can be
monitored and alerted on.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class MetricsExporter:
    """Aggregates and exports operational metrics."""

    def __init__(self):
        self._hits: Dict[str, int] = {}
        self._latency: Dict[str, List[float]] = {}
        self._errors: Dict[str, int] = {}

    def record(self, module: str, latency_s: float, ok: bool = True) -> None:
        self._hits[module] = self._hits.get(module, 0) + 1
        self._latency.setdefault(module, []).append(latency_s)
        if not ok:
            self._errors[module] = self._errors.get(module, 0) + 1

    def avg_latency(self, module: str) -> float:
        samples = self._latency.get(module, [])
        return round(sum(samples) / len(samples), 4) if samples else 0.0

    def error_rate(self, module: str) -> float:
        hits = self._hits.get(module, 0)
        if hits == 0:
            return 0.0
        return round(self._errors.get(module, 0) / hits, 4)

    def prometheus(self) -> str:
        """Render metrics in Prometheus text exposition format."""
        lines = ["# TYPE ixpansion_module_hits counter"]
        for module, count in sorted(self._hits.items()):
            lines.append(f'ixpansion_module_hits{{module="{module}"}} {count}')
        lines.append("# TYPE ixpansion_module_errors counter")
        for module, count in sorted(self._errors.items()):
            lines.append(f'ixpansion_module_errors{{module="{module}"}} {count}')
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        return {"modules_tracked": len(self._hits),
                "total_hits": sum(self._hits.values()),
                "total_errors": sum(self._errors.values())}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    exporter = MetricsExporter()
    return {"status": "active", "module": "metrics_exporter",
            **exporter.status()}
