"""Experimental waves 734–736."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave734_constellation_gravity as w734
import wave735_antimeme_vaccine as w735
import wave736_silent_broadcast_lattice as w736


def test_734_gravity():
    assert w734.coherence_vitals()["wave"] == 734
    r = w734.handler({"action": "pull", "query": "temporal crystal memory"})
    assert r["status"] == "pulled" and len(r["ranking"]) >= 3


def test_735_vaccine():
    assert w735.coherence_vitals()["wave"] == 735
    r = w735.handler({"action": "scan", "limit": 5})
    assert r["status"] == "scanned" and isinstance(r["antimemes"], list)


def test_736_broadcast():
    assert w736.coherence_vitals()["wave"] == 736
    r = w736.handler({"action": "emit", "target": "ixpansion", "lines": ["TEST", "SILENT"]})
    assert r["status"] == "emitted" and r["frames"] >= 1
