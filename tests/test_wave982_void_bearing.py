"""Tests for wave982 void_bearing — silence surface, compressed memory."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave982_void_bearing as w982

def test_vitals_and_contract():
    v = w982.coherence_vitals()
    assert v["wave"] == 982
    assert v["product_surface"] == "silence"
    assert callable(w982.handler)
    assert isinstance(w982.resonates_with(), list)
    assert "wave980_hush_tide" in w982.resonates_with()

def test_fold_compresses_to_fixed_token():
    r = w982.handler({"action": "fold", "absences": ["why_not", "unsaid_edge", ""]})
    assert r["status"] == "folded"
    assert len(r["bearing"]) == 12
    assert r["absences_folded"] == 2  # empty filtered

def test_empty_is_zero_bearing():
    r = w982.handler({"action": "fold", "absences": []})
    assert r["bearing"] == "000000000000"

def test_deterministic():
    a = w982.handler({"action": "fold", "absences": ["alpha", "beta"]})["bearing"]
    b = w982.handler({"action": "fold", "absences": ["beta", "alpha"]})["bearing"]
    assert a == b  # sorted before hash
