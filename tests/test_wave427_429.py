"""Tests for Waves 427-429: Forgotten Archive, Resonance Chamber, Forking Paths."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave427_forgotten_archive as wa
import wave428_resonance_chamber as wr
import wave429_forking_paths as wf

# --- 427 Forgotten Archive ---
def test_scan_finds_artifacts():
    r = wa.scan_forgotten()
    assert "total" in r
    assert r["total"] >= 0

def test_ghost_manifests():
    wa.scan_forgotten()
    g = wa.handler({"action": "ghost"})
    if "error" not in g or g.get("error") != "archive empty":
        assert "whisper" in g or "error" in g

def test_catalog():
    wa.scan_forgotten()
    c = wa.handler({"action": "catalog"})
    assert "artifacts" in c
    assert "total" in c

def test_status_427():
    st = wa.handler({"action": "status"})
    assert "total_artifacts" in st
    assert "ghosts_manifested" in st

def test_coherence_427():
    v = wa.coherence_vitals()
    assert v["wave"] == 427

# --- 428 Resonance Chamber ---
def test_tune():
    t = wr.tune()
    assert t["tuned"] is True
    assert "frequency" in t
    assert "harmonic" in t

def test_tune_custom_frequency():
    t = wr.tune({"frequency": 528})
    assert t["frequency"] == 528.0

def test_resonate():
    wr.tune()
    r = wr.resonate()
    assert "frequency" in r
    assert "coherence" in r
    assert 0 <= r["coherence"] <= 1
    assert "body_state" in r

def test_emit():
    wr.tune()
    e = wr.handler({"action": "emit"})
    assert "emitted" in e

def test_status_428():
    wr.tune()
    st = wr.handler({"action": "status"})
    assert st["tuned"] is True
    assert "frequency" in st

def test_coherence_428():
    v = wr.coherence_vitals()
    assert v["wave"] == 428

# --- 429 Forking Paths ---
def test_branch():
    r = wf.branch()
    assert "universes" in r
    assert 2 <= r["forked"] <= 4

def test_branch_increments():
    before = wf.handler({"action": "status"})["total_branches"]
    wf.branch()
    after = wf.handler({"action": "status"})["total_branches"]
    assert after >= before + 2

def test_traverse():
    wf.branch()
    t = wf.traverse()
    assert t["traversed"] is True
    assert "committed_universe" in t

def test_traverse_specific():
    wf.branch()
    g = wf.handler({"action": "garden"})
    bid = g["branches"][-1]["branch_id"]
    t = wf.traverse(bid)
    assert t["branch_id"] == bid

def test_garden_state():
    wf.branch()
    g = wf.handler({"action": "garden"})
    assert "branches" in g
    assert "path" in g

def test_status_429():
    st = wf.handler({"action": "status"})
    assert "total_branches" in st
    assert "path_depth" in st

def test_coherence_429():
    v = wf.coherence_vitals()
    assert v["wave"] == 429

# --- Persistence ---
def test_427_persists():
    wa.scan_forgotten()
    assert (Path(__file__).parent.parent / "data" / "wave427_forgotten_archive.json").exists()

def test_428_persists():
    wr.tune()
    assert (Path(__file__).parent.parent / "data" / "wave428_resonance_chamber.json").exists()

def test_429_persists():
    wf.branch()
    assert (Path(__file__).parent.parent / "data" / "wave429_forking_paths.json").exists()

def test_action_routing_427():
    r = wa.handler({"action": "bogus"})
    assert "error" in r

def test_action_routing_428():
    r = wr.handler({"action": "bogus"})
    assert "error" in r

def test_action_routing_429():
    r = wf.handler({"action": "bogus"})
    assert "error" in r
