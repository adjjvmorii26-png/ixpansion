"""Tests for Wave 431: Homestead."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave431_homestead as wh

def _reset():
    wh.STATE_FILE.unlink(missing_ok=True)
    wh._save({"module": "wave431_homestead", "wave": 431, "anchored": None, "vigils": [], "roots": {}})

def test_anchor():
    _reset()
    r = wh.anchor({"home": "https://example.invalid/"})
    assert r["anchored"] is True
    assert r["home"] == "https://example.invalid/"
    assert len(r["roots"]) == len(wh.FOUNDATIONS)

def test_vigil_after_anchor():
    _reset()
    wh.anchor({"home": "https://example.invalid/"})
    r = wh.vigil()
    assert "checks" in r and "ok" in r
    assert r["vigil_count"] == 1

def test_status_unbegun():
    _reset()
    s = wh.status()
    assert s["anchored"] is False

def test_status_sealed():
    _reset()
    wh.anchor()
    s = wh.status()
    assert s["anchored"] is True
    assert s["vigil_count"] == 0

def test_handler_actions():
    _reset()
    assert wh.handler({"action": "status"})["anchored"] is False
    assert "error" in wh.handler({"action": "bogus"})
    assert wh.handler({"action": "anchor"})["anchored"] is True

def test_coherence():
    assert wh.coherence_vitals()["wave"] == 431
    assert wh.coherence_vitals()["coherence"] >= 0.9

def test_wave_alias_resolver_live():
    """Hyphenated wave dashboards must resolve through the live dispatcher."""
    import importlib.util
    spec = importlib.util.find_spec("api.index")
    assert spec is not None
    import json as _json
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent.parent))
    from api.index import handler
    for path in ["/api/resonance-chamber?action=status",
                 "/api/forking-paths?action=status",
                 "/api/homestead?action=status"]:
        r = handler({"path": path, "raw_path": path})
        assert "error" not in r, f"{path} -> {r}"
