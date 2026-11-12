"""Small contract test for Wave 676 Hush Membrane.

Lab-only. Does not gate ALEPH CI.
"""
import sys
from pathlib import Path

# allow importing from api/
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave676_hush_membrane as w676


def test_coherence_vitals_shape():
    v = w676.coherence_vitals()
    assert v["wave"] == 676
    assert v["module"] == "wave676_hush_membrane"
    assert v["ok"] is True
    assert "persona" in v


def test_resonates_with():
    r = w676.resonates_with()
    assert isinstance(r, list)
    assert len(r) >= 1


def test_handler_hush_surface():
    out = w676.handler({"action": "absorb", "signal": "noise that must become memory"})
    assert out.get("status") in ("hushed", "empty")
    assert out.get("surface") == "silence" or out.get("hush") is True
    # product surface remains silence
    surface = w676.handler({"action": "surface"})
    assert surface.get("status") == "silence"
    assert surface.get("surface") == "silence"


def test_status_returns_dict():
    s = w676.handler({"action": "status"})
    assert isinstance(s, dict)
    assert s.get("wave") == 676 or "wave" in s
