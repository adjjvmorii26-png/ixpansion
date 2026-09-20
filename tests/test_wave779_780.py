"""Waves 779–780 tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave779_phaseshift_router as w779
import wave780_pentaxis_projection as w780


def test_779_route():
    w779.DATA.mkdir(parents=True, exist_ok=True)
    w779.STATE_FILE.write_text(
        '{"wave":779,"name":"phaseshift_router","routes":0,"last_phase":null,"status":"test"}'
    )
    assert w779.coherence_vitals()["wave"] == 779
    r = w779.handler({"action": "route", "hint": "chaos soak", "load": 0.9})
    assert r["phase"] == "plasma"
    assert r["audio"] is False
    s = w779.handler({"action": "route", "hint": "compile tests", "load": 0.1})
    assert s["phase"] == "solid"


def test_780_project():
    w780.DATA.mkdir(parents=True, exist_ok=True)
    w780.STATE_FILE.write_text(
        '{"wave":780,"name":"pentaxis_projection","projections":0,"status":"test"}'
    )
    assert w780.coherence_vitals()["formula"] == "P(Σ,Τ,Ψ,Μ,Ω)→R²"
    p = w780.handler({"action": "project", "sigma": 1, "tau": 0, "psi": 0, "mu": 0, "omega": 0})
    assert p["status"] == "projected"
    assert 0.0 <= p["x"] <= 1.0 and 0.0 <= p["y"] <= 1.0
    assert p["audio"] is False
