"""Wave 700 still_interval — silence duration as product surface."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave700_still_interval as w700


def test_contract():
    v = w700.coherence_vitals()
    assert v["wave"] == 700
    assert v["ok"] is True
    names = w700.resonates_with()
    assert "wave681_hush_membrane" in names
    assert all(isinstance(n, str) for n in names)


def test_mark_and_hold():
    r = w700.handler({"action": "mark", "interval_s": 4.2, "note": "after hush"})
    assert r["status"] == "marked"
    assert r["silent"] is True
    assert r["surface"] == ""
    assert r["grain"].startswith("still:")
    held = w700.handler({"action": "hold"})
    assert held["status"] == "held"
    assert held["memory"].startswith("still:")


def test_loud_interval_emits_grain():
    r = w700.handler({"action": "mark", "interval_s": 0.2})
    assert r["status"] == "marked"
    assert r["silent"] is False
    assert r["surface"].startswith("breath:")
