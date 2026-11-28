"""Wave 983 Absence Compass — small contract test."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave983_absence_compass as w983


def test_coherence_vitals():
    v = w983.coherence_vitals()
    assert v["wave"] == 983
    assert v["name"] == "absence_compass"
    assert v["product_surface"] == "hush"
    assert v["status"] == "active"


def test_handler_compresses_absences():
    r = w983.handler({"absences": ["missing_pulse", "empty_slot", "withheld"]})
    assert r["wave"] == 983
    assert r["organ"] == "absence_compass"
    assert len(r["residue"]) == 8
    assert r["product_surface"] == "hush"
    assert "dx" in r["bearing"] and "dy" in r["bearing"]
    assert abs(r["bearing"]["dx"]) <= 0.42
    assert abs(r["bearing"]["dy"]) <= 0.42


def test_empty_is_zero_residue():
    r = w983.handler({})
    assert r["residue"] == "00000000"
    assert r["density"] == 0.0
    assert r["recommend"].startswith("Orient")


def test_resonates_with_council():
    peers = w983.resonates_with()
    assert "wave671_harmony_braid" in peers
    assert "wave980_hush_tide" in peers
