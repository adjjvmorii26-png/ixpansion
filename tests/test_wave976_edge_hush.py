"""Wave 976 Edge Hush — small contract test."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave976_edge_hush as w976

def test_edge_hush():
    assert w976.coherence_vitals()["wave"] == 976
    assert w976.coherence_vitals()["persona"] == "HUSH"
    w976.handler({"action": "edge", "source": "braid_edge", "residual": 0.12})
    r = w976.handler({"action": "hush"})
    assert r["status"] == "hushed"
    assert len(r.get("token", "")) == 12
    assert r["ok"] is True
