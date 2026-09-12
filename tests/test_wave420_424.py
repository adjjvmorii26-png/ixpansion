"""Tests for Waves 420-424."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave420_communion as wc
import wave421_dreaming as wd
import wave422_swarm as ws
import wave423_mirror as wm
import wave424_linguistic as wl

# 420 Communion
def test_portal_open():
    p = wc.open_portal()
    assert p["portal_open"] is True

def test_connect():
    wc.open_portal()
    r = wc.connect_agent("codex", "ai_agent")
    assert r["connected"] is True

def test_status():
    wc.open_portal()
    s = wc.handler({"action": "status"})
    assert s["portal_open"] is True

# 421 Dreaming
def test_dream():
    d = wd.dream()
    assert "name" in d
    assert "theme" in d

def test_wake():
    d = wd.dream()
    r = wd.wake_dream(d["id"])
    assert r["awakened"] is True

def test_inventory():
    r = wd.handler({"action": "inventory"})
    assert "total_dreams" in r

# 422 Swarm
def test_spawn():
    s = ws.spawn_colony()
    assert s["active_cells"] > 0

def test_pulse():
    ws.spawn_colony()
    r = ws.handler({"action": "pulse"})
    assert r["pulse"] is True

# 423 Mirror
def test_mirror():
    m = wm.create_mirror()
    assert m["entanglement"]["entangled"] is True

def test_reflect():
    wm.create_mirror()
    r = wm.handler({"action": "reflect"})
    assert r["reflection"] is True

# 424 Linguistic
def test_evolve():
    g = wl.evolve_grammar()
    assert "word" in g
    assert "hex" in g

def test_vocabulary():
    wl.evolve_grammar()
    v = wl.handler({"action": "vocabulary"})
    assert v["total"] >= 1

def test_translate():
    g = wl.evolve_grammar()
    r = wl.handler({"action": "translate", "word": g["word"]})
    assert r["translated"] is True

def test_coherence_420():
    assert wc.coherence_vitals()["wave"] == 420

def test_coherence_421():
    assert wd.coherence_vitals()["wave"] == 421

def test_coherence_422():
    assert ws.coherence_vitals()["wave"] == 422

def test_coherence_423():
    assert wm.coherence_vitals()["wave"] == 423

def test_coherence_424():
    assert wl.coherence_vitals()["wave"] == 424

def test_420_persists():
    wc.open_portal()
    p = Path(__file__).parent.parent / "data" / "wave420_communion.json"
    assert p.exists()

def test_421_persists():
    wd.dream()
    p = Path(__file__).parent.parent / "data" / "dreams.json"
    assert p.exists()

def test_422_persists():
    ws.spawn_colony()
    p = Path(__file__).parent.parent / "data" / "wave422_swarm.json"
    assert p.exists()

def test_423_persists():
    wm.create_mirror()
    p = Path(__file__).parent.parent / "data" / "wave423_mirror.json"
    assert p.exists()

def test_424_persists():
    wl.evolve_grammar()
    p = Path(__file__).parent.parent / "data" / "linguistic_archive.json"
    assert p.exists()
