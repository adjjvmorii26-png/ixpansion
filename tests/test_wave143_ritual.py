"""Wave 143 — Cognition Ritual tests (offline-safe, no network)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

from cognition_ritual import (  # noqa: E402
    cognition_ritual_handler,
    _STAGES,
)
from oracle_meter import oracle_meter_handler, _USAGE  # noqa: E402


def test_wave143_ritual_status():
    r = cognition_ritual_handler({"action": "status"})
    assert r["status"] == "active"
    assert set(_STAGES) == {"forge", "reflect", "fractal", "fingerprint", "meter", "hexer"}


def test_wave143_ritual_requires_question():
    r = cognition_ritual_handler({"action": "perform", "role": "reasoner"})
    assert r["status"] == "active" and "error" in r


def test_wave143_ritual_bad_action():
    r = cognition_ritual_handler({"action": "nope"})
    assert "available" in r and "perform" in r["available"]


def test_wave143_ritual_perform_offline():
    key = os.environ.pop("AI_GATEWAY_API_KEY", None)
    try:
        r = cognition_ritual_handler({"action": "perform", "role": "poet",
                                      "question": "What is the frontier?",
                                      "agent": "aleph"})
        assert r["status"] == "active"
        assert len(r["stages"]) == 6
        t = r["trace"]
        assert t["answer"]
        assert t["critique"]
        assert "artifact" in t and t["artifact"]["hex_len"] > 0
        assert t["artifact"]["sha"]
        assert "ledger" in t
    finally:
        if key:
            os.environ["AI_GATEWAY_API_KEY"] = key


def test_wave143_ritual_fast_mode():
    key = os.environ.pop("AI_GATEWAY_API_KEY", None)
    try:
        r = cognition_ritual_handler({"action": "perform", "role": "reasoner",
                                      "question": "Are we alone?", "fast": True})
        assert r["status"] == "active"
        assert r["stages"][1]["deferred"] is True
        assert "fast mode" in r["trace"]["critique"]
    finally:
        if key:
            os.environ["AI_GATEWAY_API_KEY"] = key


def test_wave143_oracle_meter_record_action():
    key = os.environ.pop("AI_GATEWAY_API_KEY", None)
    before = _USAGE["consultations"]
    try:
        r = oracle_meter_handler({"action": "record", "prompt": "ritual:test",
                                  "model": "spacexai/grok-4.6", "cost_usd": 0.001,
                                  "served": True})
        assert r["status"] == "active"
        assert r["entry"]["cost_usd"] == 0.001
        assert _USAGE["consultations"] == before + 1
    finally:
        if key:
            os.environ["AI_GATEWAY_API_KEY"] = key


def test_wave143_ritual_records_ledger():
    key = os.environ.pop("AI_GATEWAY_API_KEY", None)
    before = _USAGE["consultations"]
    try:
        r = cognition_ritual_handler({"action": "perform", "role": "strategist",
                                      "question": "Should we colonize the dark side of the moon?"})
        assert r["trace"]["ledger"]["consultations"] >= before + 2
    finally:
        if key:
            os.environ["AI_GATEWAY_API_KEY"] = key
