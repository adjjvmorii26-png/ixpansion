"""Organism pulse engine + wave 460 bridge."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "lab" / "ops"))
sys.path.insert(0, str(ROOT / "api"))

from organism_pulse_engine import build_index, bloom_has, fingerprint, pulse
import wave460_pulse_engine_bridge as w460


def test_index_and_bloom():
    idx = build_index()
    assert idx["count"] >= 1
    assert isinstance(idx["waves"], list)
    if idx["waves"]:
        assert bloom_has(idx, idx["waves"][0]) is True
        assert bloom_has(idx, 999999) is False


def test_fingerprint_stable():
    a = fingerprint([{"module": "x", "ok": True, "wave": 1}])
    b = fingerprint([{"module": "x", "ok": True, "wave": 1}])
    c = fingerprint([{"module": "x", "ok": True, "wave": 2}])
    assert a == b and a != c
    assert len(a) == 64


def test_pulse_fast():
    r = pulse(force=True, max_modules=30)
    assert r["status"] == "pulse"
    assert r["ms"] < 30_000
    assert "fingerprint" in r
    r2 = pulse(force=False, max_modules=30)
    assert r2["cache_hits"] >= 0
    assert r2["fingerprint"] == r["fingerprint"]


def test_460_bridge():
    assert w460.coherence_vitals()["wave"] == 460
    r = w460.handler({"action": "index"})
    assert r["status"] == "index" and r["count"] >= 1
