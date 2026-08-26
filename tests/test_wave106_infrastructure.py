from __future__ import annotations
"""Wave 106 — Infrastructure Completeness Tests."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Request Validator ─────────────────────────────────────────────

def test_validate_valid():
    from api.request_validator import RequestValidator
    v = RequestValidator()
    result = v.validate("agent_rent", {"agent_id": "scout", "renter": "user", "hours": 2})
    assert result["valid"]

def test_validate_missing_field():
    from api.request_validator import RequestValidator
    v = RequestValidator()
    result = v.validate("agent_rent", {"agent_id": "scout"})
    assert not result["valid"]
    assert "missing" in result["errors"][0]


# ── Response Cache ────────────────────────────────────────────────

def test_cache_set_get():
    from api.response_cache import ResponseCache
    c = ResponseCache()
    c.set("key1", {"data": "value1"})
    result = c.get("key1")
    assert result["hit"]
    assert result["value"]["data"] == "value1"

def test_cache_miss():
    from api.response_cache import ResponseCache
    c = ResponseCache()
    result = c.get("nonexistent")
    assert not result["hit"]

def test_cache_invalidate():
    from api.response_cache import ResponseCache
    c = ResponseCache()
    c.set("key1", "value")
    c.invalidate("key1")
    result = c.get("key1")
    assert not result["hit"]

def test_cache_stats():
    from api.response_cache import ResponseCache
    c = ResponseCache()
    c.set("a", 1)
    c.get("a")
    c.get("b")
    stats = c.get_stats()
    assert stats["hits"] >= 1
    assert stats["misses"] >= 1


# ── Circuit Breaker ───────────────────────────────────────────────

def test_circuit_close():
    from api.circuit_breaker_standalone import CircuitBreaker
    cb = CircuitBreaker(failure_threshold=3)
    result = cb.record_success("api")
    assert result["state"] == "closed"

def test_circuit_open():
    from api.circuit_breaker_standalone import CircuitBreaker
    cb = CircuitBreaker(failure_threshold=3)
    for _ in range(4):
        cb.record_failure("api")
    result = cb.allow_request("api")
    assert not result["allowed"]

def test_circuit_recovery():
    from api.circuit_breaker_standalone import CircuitBreaker
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0)
    cb.record_failure("api")
    cb.record_failure("api")
    import time; time.sleep(0.01)
    result = cb.allow_request("api")
    assert result["allowed"]


# ── Rate Limiter ──────────────────────────────────────────────────

def test_rate_allow():
    from api.rate_limiter import RateLimiter
    rl = RateLimiter(default_rate=60, default_burst=5)
    result = rl.allow("user_1")
    assert result["allowed"]

def test_rate_exceed():
    from api.rate_limiter import RateLimiter
    rl = RateLimiter(default_rate=60, default_burst=2)
    rl.allow("user_1")
    rl.allow("user_1")
    result = rl.allow("user_1")
    assert not result["allowed"]


# ── Request Logger ────────────────────────────────────────────────

def test_log_request():
    from api.request_logger import RequestLogger
    rl = RequestLogger()
    entry = rl.log("GET", "/api/health", 200, 12.5, "user_1")
    assert entry["method"] == "GET"
    assert entry["status"] == 200

def test_query_requests():
    from api.request_logger import RequestLogger
    rl = RequestLogger()
    rl.log("GET", "/api/health", 200, 10, "u1")
    rl.log("POST", "/api/rent", 500, 50, "u2")
    errors = rl.query(status=500)
    assert len(errors) >= 1

def test_logger_stats():
    from api.request_logger import RequestLogger
    rl = RequestLogger()
    rl.log("GET", "/a", 200, 10, "u1")
    stats = rl.stats()
    assert stats["total"] == 1


# ── Auth Middleware ────────────────────────────────────────────────

def test_register_key():
    from api.auth_middleware import AuthMiddleware
    am = AuthMiddleware()
    result = am.register_key("user_1", "pro")
    assert result["tier"] == "pro"

def test_validate_key():
    from api.auth_middleware import AuthMiddleware
    am = AuthMiddleware()
    reg = am.register_key("user_1", "admin")
    auth = am.validate_key(reg["api_key"])
    assert auth["valid"]
    assert auth["tier"] == "admin"

def test_check_permission():
    from api.auth_middleware import AuthMiddleware
    am = AuthMiddleware()
    reg = am.register_key("user_1", "free")
    perm = am.check_permission(reg["api_key"], "read")
    assert perm["allowed"]
    perm2 = am.check_permission(reg["api_key"], "delete")
    assert not perm2["allowed"]

def test_session():
    from api.auth_middleware import AuthMiddleware
    am = AuthMiddleware()
    session = am.create_session("user_1")
    valid = am.validate_session(session["session_id"])
    assert valid["valid"]


# ── Health Aggregator ─────────────────────────────────────────────

def test_health_check():
    from api.health_aggregator import HealthAggregator
    ha = HealthAggregator()
    ha.register("test_service")
    result = ha.check_all()
    assert result["overall"] in ("healthy", "degraded", "unhealthy")

def test_health_register():
    from api.health_aggregator import HealthAggregator
    ha = HealthAggregator()
    result = ha.register("api")
    assert result["registered"]


# ── WebSocket Stream ──────────────────────────────────────────────

def test_connect():
    from api.websocket_stream import WebSocketStream
    ws = WebSocketStream()
    result = ws.connect("alice")
    assert "connection_id" in result

def test_subscribe_broadcast():
    from api.websocket_stream import WebSocketStream
    ws = WebSocketStream()
    c1 = ws.connect("alice")
    c2 = ws.connect("bob")
    ws.subscribe(c1["connection_id"], "general")
    ws.subscribe(c2["connection_id"], "general")
    msg = ws.broadcast("general", "hello")
    assert msg["delivered_to"] == 2

def test_presence():
    from api.websocket_stream import WebSocketStream
    ws = WebSocketStream()
    c1 = ws.connect("alice")
    ws.subscribe(c1["connection_id"], "ch")
    presence = ws.presence("ch")
    assert "alice" in presence

def test_disconnect():
    from api.websocket_stream import WebSocketStream
    ws = WebSocketStream()
    c1 = ws.connect("alice")
    ws.subscribe(c1["connection_id"], "ch")
    ws.disconnect(c1["connection_id"])
    assert "alice" not in ws.presence("ch")


# ── Handler smoke tests ───────────────────────────────────────────

def test_all_handlers():
    from api.request_validator import handler as h1
    from api.response_cache import handler as h2
    from api.circuit_breaker_standalone import handler as h3
    from api.rate_limiter import handler as h4
    from api.request_logger import handler as h5
    from api.auth_middleware import handler as h6
    from api.health_aggregator import handler as h7
    from api.websocket_stream import handler as h8
    for h in [h1, h2, h3, h4, h5, h6, h7, h8]:
        result = h({}, {})
        assert isinstance(result, (dict, list))
