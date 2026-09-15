"""Waves 687–689 experimental arc."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave687_negative_space_atlas as w687
import wave688_dream_residue as w688
import wave689_reciprocal_hush as w689

def test_687_negative_space():
    assert w687.coherence_vitals()["wave"] == 687
    r = w687.handler({"action": "omit", "name": "audio_pipeline", "reason": "silence_doctrine"})
    assert r["status"] == "omitted"
    q = w687.handler({"action": "query", "q": "audio"})
    assert q["status"] == "queried" and len(q["hits"]) >= 1

def test_688_dream_residue():
    assert w688.coherence_vitals()["wave"] == 688
    d = w688.handler({"action": "deposit", "label": "partial_dag", "fragment": "sim\u2192evolve"})
    assert d["status"] == "deposited"
    i = w688.handler({"action": "inhale"})
    assert i["status"] == "inhaled" and "residue" in i

def test_689_reciprocal_hush():
    assert w689.coherence_vitals()["wave"] == 689
    w689.handler({"action": "offer", "side": "sell_hush", "amount": 2.0, "peer": "a"})
    w689.handler({"action": "offer", "side": "sell_void", "amount": 2.0, "peer": "b"})
    c = w689.handler({"action": "clear"})
    assert c["status"] == "cleared" and c["qty"] > 0
