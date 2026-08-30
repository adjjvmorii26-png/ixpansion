"""Wave 142 — Frontier Cognition Layer tests (offline-safe, no network)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

import gateway_ink  # noqa: E402
from cognition_forge import cognition_forge_handler  # noqa: E402
from oracle_meter import oracle_meter_handler, _USAGE, _LEDGER  # noqa: E402
from fractal_oracle import fractal_oracle_handler, _sub_questions  # noqa: E402
from cognition_fingerprint import cognition_fingerprint_handler, _analyze  # noqa: E402
from dream_hexer import dream_hexer_handler, _to_hex, _from_hex  # noqa: E402


def test_wave142_gateway_ink_unconfigured_degrades():
    key = os.environ.pop("AI_GATEWAY_API_KEY", None)
    try:
        r = gateway_ink.relay("a sufficiently long question about the frontier?")
        assert r["ok"] is False
        assert r["reason"] == "unconfigured"
        assert "shadow" in r["reply"].lower()
        assert r["model"] == "spacexai/grok-4.6"
    finally:
        if key:
            os.environ["AI_GATEWAY_API_KEY"] = key


def test_wave142_gateway_ink_custom_fallback():
    key = os.environ.pop("AI_GATEWAY_API_KEY", None)
    try:
        r = gateway_ink.relay("prompt", fallback="static answer")
        assert r["ok"] is False and r["reply"] == "static answer"
    finally:
        if key:
            os.environ["AI_GATEWAY_API_KEY"] = key


def test_wave142_cognition_forge_status():
    r = cognition_forge_handler({})
    assert r["status"] == "active"
    assert "strategist" in r["specializations"] and "poet" in r["specializations"]


def test_wave142_cognition_forge_think_degrades():
    key = os.environ.pop("AI_GATEWAY_API_KEY", None)
    try:
        r = cognition_forge_handler({"action": "think", "role": "reasoner",
                                     "prompt": "why does entropy rise?"})
        assert r["status"] == "active"
        assert r["served"] is False
        assert "cold-logic" in r["cognition"] or "reasoner" in r["cognition"]
    finally:
        if key:
            os.environ["AI_GATEWAY_API_KEY"] = key


def test_wave142_cognition_forge_bad_action():
    r = cognition_forge_handler({"action": "nope"})
    assert "available" in r and "think" in r["available"]


def test_wave142_oracle_meter_consult_degrades():
    key = os.environ.pop("AI_GATEWAY_API_KEY", None)
    before = _USAGE["consultations"]
    try:
        r = oracle_meter_handler({"action": "consult", "prompt": "tell me the future"})
        assert r["status"] == "active" and r["served"] is False
        assert _USAGE["consultations"] == before + 1
    finally:
        if key:
            os.environ["AI_GATEWAY_API_KEY"] = key


def test_wave142_oracle_meter_spend_budget():
    r = oracle_meter_handler({"action": "spend"})
    assert r["status"] == "active"
    assert r["budget"]["monthly_usd"] == 25.0
    assert 0.0 <= r["budget"]["spent_usd"] <= 25.0
    assert "ledger" in r


def test_wave142_fractal_oracle_status():
    r = fractal_oracle_handler({"action": "status"})
    assert r["status"] == "active" and r["recursive"] is True


def test_wave142_fractal_sub_questions():
    subs = _sub_questions("What is the nature of the computational frontier?", 1)
    assert len(subs) >= 1
    assert "nature" in subs[0]
    assert "What" not in subs[0]


def test_wave142_fractal_oracle_ask_degrades():
    key = os.environ.pop("AI_GATEWAY_API_KEY", None)
    try:
        r = fractal_oracle_handler({"action": "ask", "question": "What is the frontier?"})
        assert r["status"] == "active"
        assert r["depths_explored"] >= 1
        assert "root" in r
    finally:
        if key:
            os.environ["AI_GATEWAY_API_KEY"] = key


def test_wave142_cognition_fingerprint_analyze():
    profile = _analyze("The incandescent and luminous frontier radiates transcendent meaning.", "x")
    assert "verbosity" in profile and "neologism" in profile and "depth" in profile


def test_wave142_cognition_fingerprint_sample_degrades():
    key = os.environ.pop("AI_GATEWAY_API_KEY", None)
    try:
        r = cognition_fingerprint_handler({"action": "sample", "agent": "aleph"})
        assert r["status"] == "active" and "fingerprint" in r
    finally:
        if key:
            os.environ["AI_GATEWAY_API_KEY"] = key


def test_wave142_dream_hexer_bind_unbind_roundtrip():
    r = dream_hexer_handler({"action": "bind", "text": "the void dreams in hex"})
    assert r["status"] == "active"
    hexgram = r["dream"]["hex"]
    assert "sha" in r["dream"]
    back = dream_hexer_handler({"action": "unbind", "hex": hexgram})
    assert back["text"] == "the void dreams in hex"


def test_wave142_dream_hexer_hex_helpers():
    assert _from_hex(_to_hex("aleph")) == "aleph"
    assert _to_hex("") == ""


def test_wave142_dream_hexer_hexit_degrades():
    key = os.environ.pop("AI_GATEWAY_API_KEY", None)
    try:
        r = dream_hexer_handler({"action": "hexit", "text": "compute order from chaos"})
        assert r["status"] == "active" and "hex" in r and r["hex_len"] > 0
    finally:
        if key:
            os.environ["AI_GATEWAY_API_KEY"] = key


def test_wave142_dream_hexer_recent():
    dream_hexer_handler({"action": "bind", "text": "recorded dream"})
    r = dream_hexer_handler({"action": "recent"})
    assert r["status"] == "active" and r["total"] >= 1
    assert r["dreams"][0]["text"] == "recorded dream"


def test_wave142_gateway_ink_forwards_reasoning_effort(monkeypatch):
    """relay passes reasoning_effort through to _chat."""
    captured = {}

    def fake_chat(model, messages, max_tokens, temperature, system=None, reasoning_effort=None):
        captured["effort"] = reasoning_effort
        return {"reply": "fast reply", "usage": {}, "latency_ms": 10}

    monkeypatch.setenv("AI_GATEWAY_API_KEY", "k")
    monkeypatch.setattr(gateway_ink, "_gateway_key", lambda: "k")
    monkeypatch.setattr(gateway_ink, "_chat", fake_chat)
    r = gateway_ink.relay("hello", reasoning_effort="low")
    assert r["ok"] is True and r["reply"] == "fast reply"
    assert captured["effort"] == "low"


def test_wave142_cognition_forge_reasoning_effort(monkeypatch):
    import cognition_forge as cf_module
    captured = {}

    def fake_relay(prompt, model=None, system=None, max_tokens=220,
                   fallback=None, reasoning_effort=None):
        captured["effort"] = reasoning_effort
        return {"ok": True, "reply": "thoughtful"}

    class GI:
        relay = staticmethod(fake_relay)
    monkeypatch.setattr(cf_module, "gateway_ink", GI())
    r = cf_module.cognition_forge_handler({"action": "think", "prompt": "x",
                                            "reasoning_effort": "low"})
    assert r["status"] == "active"
    assert captured["effort"] == "low"


def test_wave142_dream_hexer_bind_unbind_roundtrip():
    r = dream_hexer_handler({"action": "bind", "text": "the void dreams in hex"})
    assert r["status"] == "active"
    hexgram = r["dream"]["hex"]
    assert "sha" in r["dream"]
    back = dream_hexer_handler({"action": "unbind", "hex": hexgram})
    assert back["text"] == "the void dreams in hex"


def test_wave142_dream_hexer_hex_helpers():
    assert _from_hex(_to_hex("aleph")) == "aleph"
    assert _to_hex("") == ""


def test_wave142_dream_hexer_hexit_degrades():
    key = os.environ.pop("AI_GATEWAY_API_KEY", None)
    try:
        r = dream_hexer_handler({"action": "hexit", "text": "compute order from chaos"})
        assert r["status"] == "active" and "hex" in r and r["hex_len"] > 0
    finally:
        if key:
            os.environ["AI_GATEWAY_API_KEY"] = key


def test_wave142_dream_hexer_recent():
    dream_hexer_handler({"action": "bind", "text": "recorded dream"})
    r = dream_hexer_handler({"action": "recent"})
    assert r["status"] == "active" and r["total"] >= 1
    assert r["dreams"][0]["text"] == "recorded dream"


def test_wave142_gateway_ink_forwards_reasoning_effort(monkeypatch):
    """relay passes reasoning_effort through to _chat."""
    captured = {}

    def fake_chat(model, messages, max_tokens, temperature, system=None, reasoning_effort=None):
        captured["effort"] = reasoning_effort
        return {"reply": "fast reply", "usage": {}, "latency_ms": 10}

    monkeypatch.setenv("AI_GATEWAY_API_KEY", "k")
    monkeypatch.setattr(gateway_ink, "_gateway_key", lambda: "k")
    monkeypatch.setattr(gateway_ink, "_chat", fake_chat)
    r = gateway_ink.relay("hello", reasoning_effort="low")
    assert r["ok"] is True and r["reply"] == "fast reply"
    assert captured["effort"] == "low"
