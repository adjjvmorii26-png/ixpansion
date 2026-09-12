"""Tests for Wave 426 Causal Weaving."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave426_causal_weave as wc

def test_weave():
    t = wc.weave()
    assert "thread_id" in t
    assert "future_event" in t
    assert "past_anchor" in t
    assert t["direction"] == "retroactive"

def test_weave_custom():
    t = wc.weave({"future_event": "next_merge", "past_anchor": "first_commit"})
    assert t["future_event"] == "next_merge"
    assert t["past_anchor"] == "first_commit"

def test_weave_increments_total():
    before = wc.handler({"action": "status"})["total_threads"]
    wc.weave()
    after = wc.handler({"action": "status"})["total_threads"]
    assert after == before + 1

def test_resolve():
    wc.weave()
    r = wc.resolve()
    assert r["resolved"] is True
    assert "paradox_cost" in r
    assert 0 <= r["paradox_cost"] <= 1

def test_resolve_specific():
    wc.weave()
    reg = wc.handler({"action": "registry"})
    tid = reg["threads"][-1]["thread_id"]
    r = wc.resolve(tid)
    assert r["resolved"] is True

def test_registry():
    wc.weave()
    reg = wc.handler({"action": "registry"})
    assert reg["total"] >= 1
    assert isinstance(reg["threads"], list)

def test_status():
    st = wc.handler({"action": "status"})
    assert "total_threads" in st
    assert "resolved" in st

def test_coherence():
    v = wc.coherence_vitals()
    assert v["wave"] == 426
    assert v["status"] == "active"

def test_persists():
    wc.weave()
    p = Path(__file__).parent.parent / "data" / "wave426_causal_weave.json"
    assert p.exists()
    d = json.loads(p.read_text())
    assert "threads" in d

def test_action_routing():
    r = wc.handler({"action": "bogus"})
    assert "error" in r
    assert "valid" in r

def test_resonates():
    assert wc.resonates_with("causal")
    assert wc.resonates_with("weave")
