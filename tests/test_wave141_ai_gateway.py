"""Wave 141 — AI Gateway & Frontier Cognition tests."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

from ai_gateway import (  # noqa: E402
    ai_gateway_handler,
    _estimate_tokens,
    _estimate_cost,
    DEFAULT_MODEL,
)


def test_wave141_status_unconfigured():
    key = os.environ.pop("AI_GATEWAY_API_KEY", None)
    try:
        r = ai_gateway_handler({"action": "status"})
        assert r["status"] == "unconfigured"
        assert r["catalog_models"] == 0
        assert "AI_GATEWAY_API_KEY" in r["hint"]
    finally:
        if key:
            os.environ["AI_GATEWAY_API_KEY"] = key


def test_wave141_estimate():
    r = ai_gateway_handler({"action": "estimate", "model": "spacexai/grok-4.6",
                            "input": "hello " * 40, "output": "hi"})
    assert r["status"] == "ok"
    assert r["model"] == "spacexai/grok-4.6"
    assert r["tokens_in_est"] > 0 and r["tokens_out_est"] > 0
    assert isinstance(r["cost_usd_est"], float)


def test_wave141_estimate_tokens():
    assert _estimate_tokens("") == 0
    assert _estimate_tokens("hello world test sentence") >= 1


def test_wave141_cost_model():
    c = _estimate_cost("spacexai/grok-4.6", "a" * 400, "b" * 400)
    assert c["tokens_in_est"] >= 50
    assert c["tokens_out_est"] >= 50
    assert c["cost_usd_est"] > 0


def test_wave141_bad_action():
    r = ai_gateway_handler({"action": "nope"})
    assert r["status"] == "error"
    assert "unknown action" in r["error"]
    assert "handshake" in r["available"]


def test_wave141_handshake_monkeypatched(monkeypatch):
    """End-to-end handshake with a stubbed gateway (no network in CI)."""

    def fake_request(path, body=None, timeout=60.0):
        reply = "LINKED"
        return {
            "model": path.split("/")[-1] or DEFAULT_MODEL,
            "choices": [{"message": {"content": reply}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 1, "total_tokens": 11},
        }, 42.0

    monkeypatch.setattr(os.environ, "get", lambda k, d=None: "test-key" if k == "AI_GATEWAY_API_KEY" else d)
    monkeypatch.setattr("ai_gateway._request", fake_request)
    r = ai_gateway_handler({"action": "handshake", "model": DEFAULT_MODEL})
    assert r["status"] == "linked"
    assert r["reply"] == "LINKED"
    assert r["latency_ms"] == 42.0


def test_wave141_handler_default_action():
    r = ai_gateway_handler({})
    assert r["status"] in ("configured", "unconfigured")
