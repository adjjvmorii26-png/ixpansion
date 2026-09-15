"""Wave 681 hush_membrane — silence surface + compression memory."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave681_hush_membrane as w681

def test_vitals_and_resonance():
    v = w681.coherence_vitals()
    assert v["wave"] == 681 and v["ok"] is True
    names = w681.resonates_with()
    assert "wave675_consensus_bloom" in names
    assert "wave680_organism_horizon" in names

def test_hush_emits_when_coherent():
    r = w681.handler({
        "action": "hush",
        "pulse": "council bloom holds the hush",
        "coherence": 0.9,
    })
    assert r["status"] == "hushed"
    assert r["silent"] is False
    assert r["surface"].startswith("council/bloom/holds#")
    assert r["chars_out"] < r["chars_in"]

def test_hush_withholds_below_threshold():
    r = w681.handler({
        "action": "hush",
        "pulse": "noise that should not surface",
        "coherence": 0.1,
    })
    assert r["status"] == "hushed"
    assert r["silent"] is True
    assert r["surface"] == ""
    rec = w681.handler({"action": "recall"})
    assert rec["status"] == "recalled"
    assert rec["last"]["token"]
