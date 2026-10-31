"""Wave 973 Gap Lattice — silent intervals as product surface."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave973_gap_lattice as w973

def test_gap_lattice_contract():
    assert w973.coherence_vitals()["wave"] == 973
    assert "wave972_hush_vector" in w973.resonates_with()
    r = w973.handler({"action": "record", "left": "wave671_harmony_braid", "right": "wave675_consensus_bloom", "width": 0.62})
    assert r["status"] == "recorded"
    w973.handler({"action": "record", "left": "wave672_root_archive", "right": "wave674_dawn_ledger", "width": 0.41})
    w = w973.handler({"action": "weave"})
    assert w["status"] == "woven"
    assert w973.coherence_vitals()["lattice"] >= 1
