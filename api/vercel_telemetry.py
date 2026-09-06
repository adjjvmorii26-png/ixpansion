"""Wave 451 — Vercel Telemetry.

Awareness organ for the Vercel Metrics integration. Tracks which metrics
the organism records via the @vercel/functions Metric API and exposes
them as a living module:

  /vitals?name=query.duration_ms&value=100&plan=pro

Each metric recorded on Vercel surfaces in Vercel Observability. This
organ keeps the *intent* catalog — the metrics the organism promises
to measure — and reports on the telemetry health of the ecosystem.
"""
from __future__ import annotations
import time
from typing import Any, Dict, List, Optional

METRIC_CATALOG = [
    {"name": "query.duration_ms", "unit": "ms", "plan": "pro", "default_tag": "wave451"},
    {"name": "wave.growth", "unit": "count", "plan": "pro", "default_tag": "evolution"},
    {"name": "vitals.health", "unit": "count", "plan": "pro", "default_tag": "health"},
    {"name": "module.coherence", "unit": "0-1", "plan": "pro", "default_tag": "resonance"},
    {"name": "capybara.cycles", "unit": "count", "plan": "pro", "default_tag": "calm"},
    {"name": "silence.predictions", "unit": "count", "plan": "pro", "default_tag": "luma"},
    {"name": "error.crafts", "unit": "count", "plan": "pro", "default_tag": "luma"},
]

RECORDED_EVENTS: List[Dict[str, Any]] = []
MAX_EVENTS = 300


def record(name: str, value: float, tag: Optional[str] = None) -> Dict[str, Any]:
    """Log a metric recording (mirrors the /vitals Node endpoint)."""
    entry = {
        "metric": name,
        "value": value,
        "tags": {"plan": "pro", "organism": "ixpansion", "tag": tag} if tag else {"plan": "pro", "organism": "ixpansion"},
        "recorded_at": time.time(),
        "endpoint": f"/vitals?name={name}&value={value}" + (f"&tag={tag}" if tag else ""),
    }
    RECORDED_EVENTS.append(entry)
    if len(RECORDED_EVENTS) > MAX_EVENTS:
        RECORDED_EVENTS.pop(0)
    return entry


def catalog() -> Dict[str, Any]:
    """The metrics the organism promises to measure on Vercel."""
    return {
        "metrics": METRIC_CATALOG,
        "total_metrics": len(METRIC_CATALOG),
        "runtime": "@vercel/node (telemetry/metrics_collector.mjs)",
        "output": "Vercel Observability",
    }


def health() -> Dict[str, Any]:
    """Telemetry organ health."""
    return {
        "organ": "vercel_telemetry",
        "status": "recording" if RECORDED_EVENTS else "ready",
        "events_logged": len(RECORDED_EVENTS),
        "metrics_promised": len(METRIC_CATALOG),
        "latest": RECORDED_EVENTS[-1] if RECORDED_EVENTS else None,
    }


def coherence_vitals() -> Dict[str, Any]:
    return health()


def resonates_with() -> List[str]:
    return [
        "metrics_exporter", "module_analytics", "usage_dashboard",
        "revenue_oracle", "affiliate_engine", "analytics",
        "telemetry_anomaly_oracle", "aleph_bot", "capybara_core",
    ]


def handler(payload=None, context=None):
    data = payload or {}
    action = data.get("action", "health")
    if action == "catalog" or data.get("path") in ("/catalog", "/metrics"):
        return catalog()
    elif action == "record":
        return record(data.get("name", "query.duration_ms"), float(data.get("value", 100)), data.get("tag"))
    return health()
