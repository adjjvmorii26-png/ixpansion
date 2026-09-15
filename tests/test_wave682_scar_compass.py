"""Wave 682 Scar Compass."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave682_scar_compass as m

def test_vitals():
    v = m.coherence_vitals()
    assert v["wave"] == 682 and v["ok"]

def test_mark_heading():
    r = m.handler({"action": "mark", "label": "vercel_routes", "before": 754, "after": 89})
    assert r["status"] == "marked"
    assert r["scar"]["heal_ratio"] > 0.8
    h = m.handler({"action": "heading"})
    assert h["heading"] is not None

def test_resonates():
    assert "wave674_dawn_ledger" in m.resonates_with()
