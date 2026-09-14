"""Tests for OmniRouter (Wave 621)."""
import pytest
from api.omnirouter import (
    OmniRouter, CircuitBreaker, Route, handler, coherence_vitals,
    DEFAULT_ROUTES, _ensure_defaults,
)


class TestCircuitBreaker:
    def test_initial_closed(self):
        cb = CircuitBreaker()
        assert cb.is_open() is False

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(threshold=3)
        for _ in range(3):
            cb.record_failure()
        assert cb.is_open() is True

    def test_resets_on_success(self):
        cb = CircuitBreaker(threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb.is_open() is False
        assert cb.failures == 0

    def test_to_dict(self):
        cb = CircuitBreaker()
        d = cb.to_dict()
        assert "failures" in d
        assert "closed" in d


class TestRoute:
    def test_record_call_success(self):
        r = Route("test", "http_api", "hex_runtime")
        r.record_call(True, 2.5)
        assert r.metrics["total_calls"] == 1
        assert r.metrics["successes"] == 1
        assert r.success_rate == 1.0

    def test_record_call_failure(self):
        r = Route("test", "http_api", "hex_runtime")
        r.record_call(False, 50.0)
        assert r.metrics["failures"] == 1
        assert r.success_rate == 0.0

    def test_to_dict(self):
        r = Route("test", "http_api", "hex_runtime")
        d = r.to_dict()
        assert d["route_id"] == "test"
        assert d["source"] == "http_api"


class TestOmniRouter:
    def test_register_and_remove(self):
        rt = OmniRouter()
        rt.register_route("r1", "http_api", "hex_runtime")
        assert "r1" in rt.routes
        assert rt.remove_route("r1")
        assert "r1" not in rt.routes

    def test_get_routes_for_source(self):
        rt = OmniRouter()
        rt.register_route("r1", "http_api", "hex_runtime", priority=2)
        rt.register_route("r2", "http_api", "hex_cathedral", priority=1)
        rt.register_route("r3", "cli", "hex_runtime")
        routes = rt.get_routes_for_source("http_api")
        assert len(routes) == 2
        assert routes[0].route_id == "r1"  # higher priority first

    def test_route_request(self):
        rt = OmniRouter()
        rt.register_route("r1", "http_api", "hex_runtime")
        result = rt.route_request("http_api", {})
        assert result["ok"] is True
        assert result["route"] == "r1"

    def test_route_request_no_routes(self):
        rt = OmniRouter()
        result = rt.route_request("unknown", {})
        assert result["ok"] is False

    def test_route_request_all_circuits_open(self):
        rt = OmniRouter()
        rt.register_route("r1", "http_api", "hex_runtime")
        rt.routes["r1"].breaker.failures = 10
        rt.routes["r1"].breaker.closed = False
        result = rt.route_request("http_api", {})
        assert result["ok"] is False
        assert "circuits open" in result["error"]

    def test_learn_promotes(self):
        rt = OmniRouter()
        r = rt.register_route("r1", "http_api", "hex_runtime")
        for _ in range(5):
            r.record_call(True, 1.0)
        changes = rt.learn()
        assert len(changes) == 1
        assert "promoted" in changes[0]

    def test_learn_demotes(self):
        rt = OmniRouter()
        r = rt.register_route("r1", "http_api", "hex_runtime", weight=5)
        for _ in range(5):
            r.record_call(False, 100.0)
        changes = rt.learn()
        assert len(changes) == 1
        assert "demoted" in changes[0]

    def test_get_stats(self):
        rt = OmniRouter()
        rt.register_route("r1", "http_api", "hex_runtime")
        stats = rt.get_stats()
        assert stats["total_routes"] == 1
        assert stats["success_rate"] == 1.0


class TestHandler:
    def test_status(self):
        out = handler({"action": "status"})
        assert out["action"] == "status"
        assert out["wave"] == 621
        assert out["total_routes"] > 0

    def test_route(self):
        out = handler({"action": "route", "source": "http_api"})
        assert out["action"] == "route"
        assert out.get("ok") is True

    def test_register(self):
        out = handler({"action": "register", "route_id": "test_r", "source": "cli", "destination": "hex_runtime"})
        assert out["action"] == "register"
        assert out["route"]["route_id"] == "test_r"

    def test_remove(self):
        handler({"action": "register", "route_id": "del_me", "source": "cli", "destination": "hex_runtime"})
        out = handler({"action": "remove", "route_id": "del_me"})
        assert out["ok"] is True

    def test_routes(self):
        out = handler({"action": "routes"})
        assert out["action"] == "routes"
        assert len(out["routes"]) > 0

    def test_history(self):
        handler({"action": "route", "source": "http_api"})
        out = handler({"action": "history"})
        assert out["action"] == "history"
        assert isinstance(out["history"], list)

    def test_unknown_action(self):
        out = handler({"action": "bogus"})
        assert out["ok"] is False

    def test_register_missing_fields(self):
        out = handler({"action": "register", "route_id": ""})
        assert out["ok"] is False


class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals()
        assert v["wave"] == 621
        assert "total_routes" in v
