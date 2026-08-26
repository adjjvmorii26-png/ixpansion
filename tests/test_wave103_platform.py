from __future__ import annotations
"""Wave 103 — Platform Completeness Tests."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── OpenAPI Spec ──────────────────────────────────────────────────

def test_generate_spec():
    from api.openapi_spec import generate_spec
    spec = generate_spec()
    assert spec["openapi"] == "3.0.3"
    assert spec["info"]["version"] == "3.17.0"

def test_spec_has_paths():
    from api.openapi_spec import generate_spec
    spec = generate_spec()
    assert len(spec["paths"]) >= 40

def test_spec_has_tags():
    from api.openapi_spec import generate_spec
    spec = generate_spec()
    assert len(spec["tags"]) == 6

def test_spec_handler():
    from api.openapi_spec import handler
    result = handler({}, {})
    assert isinstance(result, dict)
    assert "paths" in result


# ── CORS Middleware ────────────────────────────────────────────────

def test_cors_apply():
    from api.cors_middleware import CORSMiddleware
    m = CORSMiddleware()
    headers = m.apply("https://example.com")
    assert "Access-Control-Allow-Origin" in headers
    assert headers["Access-Control-Allow-Origin"] == "https://example.com"

def test_cors_preflight():
    from api.cors_middleware import CORSMiddleware
    m = CORSMiddleware()
    headers = m.preflight("https://example.com")
    assert "Access-Control-Max-Age" in headers
    assert headers["Access-Control-Max-Age"] == "86400"

def test_cors_wildcard():
    from api.cors_middleware import CORSMiddleware
    m = CORSMiddleware(origins=["*"])
    headers = m.apply("https://any-origin.com")
    assert headers["Access-Control-Allow-Origin"] != ""

def test_cors_stats():
    from api.cors_middleware import CORSMiddleware
    m = CORSMiddleware()
    m.apply("https://a.com")
    m.apply("https://b.com")
    stats = m.stats()
    assert stats["request_count"] == 2

def test_cors_handler():
    from api.cors_middleware import handler
    result = handler({}, {})
    assert isinstance(result, dict)


# ── Structured Logging ────────────────────────────────────────────

def test_logger_creation():
    from api.structured_logging import get_logger
    log = get_logger("test_module")
    assert log.name == "test_module"

def test_logger_info():
    from api.structured_logging import get_logger
    log = get_logger("test_info")
    entry = log.info("test message", key="value")
    assert entry["level"] == "info"
    assert entry["message"] == "test message"

def test_logger_bind():
    from api.structured_logging import get_logger
    log = get_logger("test_bind").bind(user="alice", request_id="123")
    entry = log.info("bound entry")
    assert entry["context"]["user"] == "alice"

def test_logger_stats():
    from api.structured_logging import get_logger
    log = get_logger("test_stats")
    log.info("a")
    log.warn("b")
    log.error("c")
    stats = log.stats()
    assert stats["total_entries"] >= 3

def test_logger_filter():
    from api.structured_logging import get_logger
    log = get_logger("test_filter")
    log.info("a")
    log.warn("b")
    log.error("c")
    entries = log.get_entries(level="warn")
    assert all(e["level"] == "warn" for e in entries)

def test_logging_handler():
    from api.structured_logging import handler
    result = handler({}, {})
    assert isinstance(result, dict)


# ── Unified Health ────────────────────────────────────────────────

def test_health_check():
    from api.unified_health import check_health
    result = check_health()
    assert result["status"] in ("healthy", "degraded", "unhealthy")
    assert result["version"] == "3.17.0"

def test_health_subsystems():
    from api.unified_health import check_health
    result = check_health()
    assert result["subsystems"]["total"] >= 5
    assert result["subsystems"]["healthy"] >= 1

def test_health_latency():
    from api.unified_health import check_health
    result = check_health()
    assert result["total_latency_ms"] >= 0

def test_health_handler():
    from api.unified_health import handler
    result = handler({}, {})
    assert isinstance(result, dict)
    assert "status" in result


# ── Handler smoke tests ───────────────────────────────────────────

def test_all_new_handlers():
    from api.openapi_spec import handler as h1
    from api.cors_middleware import handler as h2
    from api.structured_logging import handler as h3
    from api.unified_health import handler as h4
    for h in [h1, h2, h3, h4]:
        result = h({}, {})
        assert isinstance(result, (dict, list))
