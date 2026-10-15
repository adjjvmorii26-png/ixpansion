"""CORS: response paths share the same origin allowlist."""
import api.cors_middleware as cm


def test_apply_uses_configured_allowlist(monkeypatch):
    monkeypatch.setenv("IXPANSION_CORS_ORIGINS", "https://example.com,https://app.example.com")
    m = cm.CORSMiddleware()
    assert "https://example.com" in m.origins
    good = m.apply("https://example.com")
    assert good.get("Access-Control-Allow-Origin") == "https://example.com"
    bad = m.apply("https://evil.example")
    assert bad.get("Access-Control-Allow-Origin") in ("", None)


def test_preflight_matches_apply_allowlist(monkeypatch):
    monkeypatch.setenv("IXPANSION_CORS_ORIGINS", "https://example.com")
    m = cm.CORSMiddleware()
    origin = "https://example.com"
    pre = m.preflight(origin) if hasattr(m, "preflight") else m.apply(origin)
    resp = m.apply(origin)
    assert pre.get("Access-Control-Allow-Origin") == resp.get("Access-Control-Allow-Origin")
    assert pre.get("Access-Control-Allow-Origin") == "https://example.com"


def test_no_wildcard_when_explicit_list(monkeypatch):
    monkeypatch.setenv("IXPANSION_CORS_ORIGINS", "https://only.example")
    m = cm.CORSMiddleware()
    headers = m.apply("https://other.example")
    assert headers.get("Access-Control-Allow-Origin") != "*"
