"""Tests for Wave 413 Underworld Path."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave413_underworld as wu

def test_grow():
    uw = wu.grow_underworld()
    assert uw["module"] == "wave413_underworld"
    assert "caverns" in uw
    assert len(uw["caverns"]) == 3

def test_status_after_grow():
    wu.handler({"action": "grow"})
    status = wu.handler({"action": "status"})
    assert "caverns" in status

def test_topology():
    wu.handler({"action": "grow"})
    topo = wu.handler({"action": "topology"})
    assert topo["wave"] == 413
    assert topo["realm"] == "underworld"
    assert "graph_stats" in topo

def test_migrate():
    wu.handler({"action": "grow"})
    m = wu.handler({"action": "migrate"})
    assert m["migrated"] is True

def test_echo_trade():
    wu.handler({"action": "grow"})
    t = wu.handler({"action": "echo_trade"})
    assert "cavern" in t
    assert "mineral" in t

def test_coherence():
    v = wu.coherence_vitals()
    assert v["status"] == "active"
    assert v["wave"] == 413

def test_action_routing():
    r = wu.handler({"action": "bogus"})
    assert "error" in r

def test_persists():
    wu.handler({"action": "grow"})
    p = Path(__file__).parent.parent / "data" / "wave413_underworld.json"
    assert p.exists()
    d = json.loads(p.read_text())
    assert "caverns" in d
