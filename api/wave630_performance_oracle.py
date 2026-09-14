"""Wave 630 — Performance Oracle: Bottleneck Prediction Engine.

The organism's crystal ball. It ingests metrics from the OmniRouter and
Resilience Mesh, models trends, and forecasts bottlenecks before they
happen. The organism stops reacting to failures and starts preventing them.

Features:
- Metric ingestion: records latency, throughput, error rates, load
- Trend analysis: linear regression over sliding windows
- Bottleneck prediction: forecasts where pressure will exceed thresholds
- Proactive suggestions: scaling actions before failure occurs
- Alert system: configurable severity levels for predicted issues
- Historical storage: metric windows persisted in state

Builds upon:
- Wave 621: OmniRouter (routing metrics source)
- Wave 622: Resilience Mesh (health metrics source)
- Wave 98: HEX Cathedral Lacery (program execution metrics)
"""
from __future__ import annotations
import json
import time
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DATA = Path(__file__).resolve().parents[1] / "data"
STATE_FILE = DATA / "wave630_performance_oracle.json"

PREDICTION_WINDOW = 100
FORECAST_HORIZON = 5
THRESHOLDS = {
    "latency_ms": 100.0,
    "error_rate": 0.1,
    "load_pct": 0.9,
    "circuit_breakers": 3,
}


class MetricPoint:
    """Single metric observation."""

    def __init__(self, name: str, value: float, ts: Optional[float] = None) -> None:
        self.name = name
        self.value = value
        self.ts = ts or time.time()


class MetricWindow:
    """Sliding window of metric observations."""

    def __init__(self, name: str, max_size: int = PREDICTION_WINDOW) -> None:
        self.name = name
        self.max_size = max_size
        self.points: List[MetricPoint] = []
        self.threshold = THRESHOLDS.get(name, float("inf"))

    def add(self, value: float, ts: Optional[float] = None) -> None:
        self.points.append(MetricPoint(self.name, value, ts))
        if len(self.points) > self.max_size:
            self.points = self.points[-self.max_size:]

    def average(self) -> float:
        if not self.points:
            return 0.0
        return sum(p.value for p in self.points) / len(self.points)

    def trend(self) -> float:
        """Linear regression slope over points. Positive = increasing."""
        n = len(self.points)
        if n < 2:
            return 0.0
        values = [p.value for p in self.points]
        mean_idx = (n - 1) / 2
        mean_val = sum(values) / n
        num = sum((i - mean_idx) * (v - mean_val) for i, v in enumerate(values))
        den = sum((i - mean_idx) ** 2 for i in range(n))
        return num / den if den != 0 else 0.0

    def forecast(self, steps: int = FORECAST_HORIZON) -> List[float]:
        """Project current trend forward."""
        slope = self.trend()
        base = self.average()
        return [base + slope * (i + 1) for i in range(steps)]

    def will_exceed_threshold(self, steps: int = FORECAST_HORIZON) -> bool:
        forecast = self.forecast(steps)
        return any(v > self.threshold for v in forecast)

    def current_severity(self) -> str:
        current = self.average()
        if current > self.threshold * 1.5:
            return "critical"
        elif current > self.threshold:
            return "warning"
        elif current > self.threshold * 0.7:
            return "elevated"
        return "normal"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "count": len(self.points),
            "average": round(self.average(), 4),
            "trend": round(self.trend(), 6),
            "current": round(self.points[-1].value, 4) if self.points else 0.0,
            "threshold": self.threshold,
            "severity": self.current_severity(),
            "will_exceed": self.will_exceed_threshold(),
            "forecast": [round(f, 4) for f in self.forecast()],
        }


class Alert:
    """A predicted bottleneck alert."""

    def __init__(self, metric_name: str, severity: str, message: str) -> None:
        self.metric_name = metric_name
        self.severity = severity
        self.message = message
        self.ts = time.time()
        self.acknowledged = False

    def to_dict(self) -> dict:
        return {
            "metric_name": self.metric_name,
            "severity": self.severity,
            "message": self.message,
            "ts": self.ts,
            "acknowledged": self.acknowledged,
        }


class PerformanceOracle:
    """Bottleneck prediction engine."""

    def __init__(self) -> None:
        self.windows: Dict[str, MetricWindow] = {}
        self.alerts: List[Alert] = []
        self.history: List[dict] = []

    def observe(self, metric_name: str, value: float) -> dict:
        if metric_name not in self.windows:
            self.windows[metric_name] = MetricWindow(metric_name)
        self.windows[metric_name].add(value)

        # Check for alert generation
        window = self.windows[metric_name]
        if window.will_exceed_threshold():
            severity = window.current_severity()
            if severity in ("warning", "critical"):
                msg = f"Predicted bottleneck: {metric_name} trending toward {window.forecast()[0]:.2f} (threshold: {window.threshold})"
                alert = Alert(metric_name, severity, msg)
                self.alerts.append(alert)
                if len(self.alerts) > 50:
                    self.alerts = self.alerts[-50:]

        return {
            "ok": True,
            "metric": metric_name,
            "value": value,
            "severity": window.current_severity(),
        }

    def get_forecast(self) -> Dict[str, dict]:
        return {name: w.to_dict() for name, w in self.windows.items()}

    def get_bottlenecks(self) -> List[dict]:
        bottlenecks = []
        for name, window in self.windows.items():
            if window.will_exceed_threshold():
                bottlenecks.append({
                    "metric": name,
                    "severity": window.current_severity(),
                    "current_avg": round(window.average(), 4),
                    "threshold": window.threshold,
                    "forecast_values": [round(f, 4) for f in window.forecast()],
                    "trend": round(window.trend(), 6),
                })
        return sorted(bottlenecks, key=lambda b: {
            "critical": 0, "warning": 1, "elevated": 2
        }.get(b["severity"], 3))

    def get_suggestions(self) -> List[str]:
        suggestions = []
        for name, window in self.windows.items():
            severity = window.current_severity()
            if severity == "critical":
                suggestions.append(
                    f"CRITICAL: Scale up {name} immediately — "
                    f"current avg {window.average():.2f} exceeds 150% of threshold {window.threshold}"
                )
            elif severity == "warning":
                suggestions.append(
                    f"WARNING: Monitor {name} closely — "
                    f"predicted to exceed threshold {window.threshold} within {FORECAST_HORIZON} cycles"
                )
            elif severity == "elevated":
                suggestions.append(
                    f"ELEVATED: {name} is trending upward — "
                    f"consider preemptive scaling at {(window.average()/window.threshold*100):.0f}% of threshold"
                )
        return suggestions

    def get_unacknowledged_alerts(self) -> List[dict]:
        return [a.to_dict() for a in self.alerts if not a.acknowledged]

    def acknowledge_alert(self, index: int) -> bool:
        unacked = self.get_unacknowledged_alerts()
        if 0 <= index < len(self.alerts):
            self.alerts[index].acknowledged = True
            return True
        return False

    def get_overall_health(self) -> dict:
        metrics = list(self.windows.values())
        if not metrics:
            return {"score": 1.0, "status": "no_data"}
        avg_severity = {"normal": 0, "elevated": 0.1, "warning": 0.5, "critical": 1.0}
        total = sum(avg_severity.get(m.current_severity(), 0) for m in metrics) / len(metrics)
        score = max(0.0, 1.0 - total)
        status = "healthy" if score > 0.8 else "elevated" if score > 0.6 else "degraded"
        return {"score": round(score, 4), "status": status, "metrics_count": len(metrics)}

    def to_dict(self) -> dict:
        return {
            "windows": {k: v.to_dict() for k, v in self.windows.items()},
            "alerts": [a.to_dict() for a in self.alerts[-20:]],
            "history": self.history[-20:],
        }


def _load() -> Tuple[PerformanceOracle, dict]:
    oracle = PerformanceOracle()
    state: dict = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            state = {}
    for name, wd in state.get("windows", {}).items():
        oracle.windows[name] = MetricWindow(name)
        oracle.windows[name].threshold = wd.get("threshold", THRESHOLDS.get(name, float("inf")))
    oracle.history = state.get("history", [])
    return oracle, state


def _save(oracle: PerformanceOracle, state: dict) -> None:
    data = {
        "windows": {k: v.to_dict() for k, v in oracle.windows.items()},
        "alerts": [a.to_dict() for a in oracle.alerts[-20:]],
        "history": oracle.history[-50:],
    }
    STATE_FILE.write_text(json.dumps(data, indent=2))


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    oracle, state = _load()

    if action == "status":
        health = oracle.get_overall_health()
        return {
            "action": "status",
            "wave": 630,
            **health,
            "metrics_tracked": len(oracle.windows),
            "active_alerts": len(oracle.get_unacknowledged_alerts()),
            "message": "Performance Oracle status",
        }

    if action == "observe":
        metric = req.get("metric", "")
        value = req.get("value", 0.0)
        if not metric:
            return {"ok": False, "error": "metric name required"}
        result = oracle.observe(metric, float(value))
        oracle.history.append({"ts": time.time(), "metric": metric, "value": float(value)})
        _save(oracle, state)
        return {"action": "observe", "wave": 630, **result}

    if action == "forecast":
        forecasts = oracle.get_forecast()
        return {"action": "forecast", "wave": 630, "forecasts": forecasts}

    if action == "bottlenecks":
        bottlenecks = oracle.get_bottlenecks()
        return {"action": "bottlenecks", "wave": 630, "bottlenecks": bottlenecks}

    if action == "suggest":
        suggestions = oracle.get_suggestions()
        return {"action": "suggest", "wave": 630, "suggestions": suggestions}

    if action == "alerts":
        alerts = oracle.get_unacknowledged_alerts()
        return {"action": "alerts", "wave": 630, "alerts": alerts}

    if action == "acknowledge":
        idx = req.get("index", 0)
        ok = oracle.acknowledge_alert(idx)
        _save(oracle, state)
        return {"action": "acknowledge", "wave": 630, "ok": ok}

    if action == "history":
        limit = req.get("limit", 20)
        return {"action": "history", "wave": 630, "history": oracle.history[-limit:]}

    return {"ok": False, "error": f"Unknown action: {action}"}


def coherence_vitals() -> dict:
    oracle, _ = _load()
    health = oracle.get_overall_health()
    return {
        "wave": 630,
        "metrics_tracked": len(oracle.windows),
        "health_score": health["score"],
        "health_status": health["status"],
        "active_alerts": len(oracle.get_unacknowledged_alerts()),
    }


def resonates_with() -> List[str]:
    return ["wave621_omnirouter", "wave622_resilience_mesh"]
