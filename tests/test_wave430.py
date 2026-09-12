"""Tests for Wave 430: Naming Ceremony."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave430_naming_ceremony as wc

def _reset():
    wc.STATE_FILE.unlink(missing_ok=True)
    wc._save({"module": "wave430_naming_ceremony", "wave": 430, "candidates": [], "votes": {}, "sealed": None, "ceremonies": 0})
    return True

def test_propose():
    _reset()
    r = wc.propose({"count": 4})
    assert r["proposed"] >= 2
    assert all(c["name"] and c["glyph"] for c in r["candidates"])
    assert all(c["resonance"] >= 0.0 for c in r["candidates"])

def test_propose_sorted_by_resonance():
    _reset()
    r = wc.propose({"count": 5})
    scores = [c["resonance"] for c in r["candidates"]]
    assert scores == sorted(scores, reverse=True)

def test_vote_after_propose():
    _reset()
    wc.propose()
    r = wc.vote()
    assert "winner" in r
    assert r["winner"] in [c["name"] for c in wc._load()["candidates"]]

def test_vote_without_propose():
    _reset()
    r = wc.vote()
    assert "error" in r

def test_seal():
    _reset()
    wc.propose()
    r = wc.seal()
    assert r["sealed"] is True
    assert r["name"]
    assert len(r["glyph"]) == 8
    assert wc.status()["sealed"] is True

def test_seal_auto_votes_if_no_candidates():
    _reset()
    r = wc.seal()
    assert r["sealed"] is True
    assert r["name"]

def test_status():
    _reset()
    s = wc.status()
    assert s["sealed"] is False
    assert "proposed" in s

def test_handler_actions():
    _reset()
    assert wc.handler({"action": "status"})["sealed"] is False
    assert "error" in wc.handler({"action": "bogus"})
    assert "proposed" in wc.handler({"action": "propose"})

def test_coherence():
    assert wc.coherence_vitals()["wave"] == 430
    assert wc.coherence_vitals()["coherence"] >= 0.9
