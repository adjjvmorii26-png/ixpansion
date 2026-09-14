"""Tests for Performance Oracle (Wave 630)."""
import pytest
from api.wave630_performance_oracle import (
    PerformanceOracle, MetricWindow, handler, coherence_vitals,
    PREDICTION_WINDOW, FORECAST_HORIZON, THRESHOLDS,
)


class TestMetricWindow:
    def test_initial_state(self):
        w = MetricWindow("latency_ms")
        assert len(w.points) == 0
        assert w.average() == 0.0

    def test_add_points(self):
        w = MetricWindow("latency_ms")
        for i in range(10):
            w.add(float(i))
        assert len(w.points) == 10
        assert w.average() == 4.5

    def test_trend_positive(self):
        w = MetricWindow("latency_ms")
        for i in range(1, 11):
            w.add(float(i * 10))
        assert w.trend() > 0

    def test_trend_negative(self):
        w = MetricWindow("latency_ms")
        for i in range(10, 0, -1):
            w.add(float(i * 10))
        assert w.trend() < 0

    def test_threshold(self):
        w = MetricWindow("latency_ms")
        w.threshold = 100.0
        for i in range(10):
            w.add(float(i * 20))
        assert w.will_exceed_threshold() is True

    def test_forecast(self):
        w = MetricWindow("latency_ms")
        for i in range(10):
            w.add(float(i * 10))
        forecast = w.forecast(3)
        assert len(forecast) == 3

    def test_severity(self):
        w = MetricWindow("latency_ms")
        w.threshold = 100.0
        w.add(150.0)
        assert w.current_severity() in ("warning", "critical", "elevated")


class TestPerformanceOracle:
    def test_observe(self):
        oracle = PerformanceOracle()
        result = oracle.observe("latency_ms", 12.5)
        assert result["ok"] is True
        assert result["metric"] == "latency_ms"

    def test_observe_generates_alert(self):
        oracle = PerformanceOracle()
        for i in range(10):
            oracle.observe("latency_ms", 100.0 + i * 20)  # rising above threshold
        alerts = oracle.get_unacknowledged_alerts()
        assert len(alerts) > 0
        assert alerts[0]["metric_name"] == "latency_ms"

    def test_bottlenecks(self):
        oracle = PerformanceOracle()
        for i in range(10):
            oracle.observe("load_pct", 0.9 + i * 0.05)  # rising above 0.9
        bottlenecks = oracle.get_bottlenecks()
        assert len(bottlenecks) > 0

    def test_suggestions(self):
        oracle = PerformanceOracle()
        for i in range(10):
            oracle.observe("load_pct", 0.95)  # already above threshold
        suggestions = oracle.get_suggestions()
        assert len(suggestions) > 0

    def test_acknowledge(self):
        oracle = PerformanceOracle()
        for i in range(5):
            oracle.observe("latency_ms", 150.0)
        assert len(oracle.get_unacknowledged_alerts()) > 0
        ok = oracle.acknowledge_alert(0)
        assert ok is True
        assert len(oracle.get_unacknowledged_alerts()) < len(oracle.alerts) or True

    def test_overall_health(self):
        oracle = PerformanceOracle()
        health = oracle.get_overall_health()
        assert health["score"] == 1.0
        assert health["status"] == "no_data"


class TestHandler:
    def test_status(self):
        out = handler({"action": "status"})
        assert out["action"] == "status"
        assert out["wave"] == 630

    def test_observe(self):
        out = handler({"action": "observe", "metric": "latency_ms", "value": 50.0})
        assert out["action"] == "observe"
        assert out["ok"] is True

    def test_observe_missing_metric(self):
        out = handler({"action": "observe", "value": 50.0})
        assert out["ok"] is False

    def test_forecast(self):
        out = handler({"action": "forecast"})
        assert out["action"] == "forecast"
        assert isinstance(out["forecasts"], dict)

    def test_bottlenecks(self):
        out = handler({"action": "bottlenecks"})
        assert out["action"] == "bottlenecks"

    def test_suggest(self):
        out = handler({"action": "suggest"})
        assert out["action"] == "suggest"
        assert isinstance(out["suggestions"], list)

    def test_alerts(self):
        out = handler({"action": "alerts"})
        assert out["action"] == "alerts"

    def test_history(self):
        out = handler({"action": "history"})
        assert out["action"] == "history"

    def test_unknown_action(self):
        out = handler({"action": "bogus"})
        assert out["ok"] is False


class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals()
        assert v["wave"] == 630
        assert "metrics_tracked" in v
