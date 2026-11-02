"""Wave 974 gap_compress — silent interval folding."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave974_gap_compress as w974

def test_gap_compress_basic():
    assert w974.coherence_vitals()["wave"] == 974
    assert w974.coherence_vitals()["ok"] is True
    r = w974.handler({"action": "compress", "gap": 12.5, "context": "between_braid_and_bloom"})
    assert r["status"] == "compressed"
    assert len(r.get("token", "")) >= 8
    assert r["gap"] == 12.5

def test_gap_compress_from_pair():
    r = w974.handler({"action": "compress", "a": 100, "b": 140})
    assert r["status"] == "compressed"
    assert r["gap"] == 40.0

def test_gap_compress_empty():
    r = w974.handler({"action": "compress", "gap": 0})
    assert r["status"] == "no_gap"
