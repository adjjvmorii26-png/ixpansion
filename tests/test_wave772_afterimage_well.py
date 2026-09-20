"""Wave 772 afterimage_well tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))

import wave772_afterimage_well as w772


def test_vitals_contract():
    v = w772.coherence_vitals()
    assert v["wave"] == 772
    assert v["name"] == "afterimage_well"
    assert v["ok"] is True
    assert v["surface"] == "silence"
    assert v["audio"] is False
    assert "wave771_caption_pipeline_bridge" in w772.resonates_with()


def test_impress_and_recall():
    r = w772.handler({"action": "impress", "note": "council22 still sealed", "frontier": 772})
    assert r["status"] == "impressed"
    assert r["residue"]["hash"]
    assert r["residue"]["bytes_out"] == 16
    rec = w772.handler({"action": "recall", "hash": r["residue"]["hash"]})
    assert rec["status"] == "recalled"
    assert rec["residue"]["note"] == "council22 still sealed"
