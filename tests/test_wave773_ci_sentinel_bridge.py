"""Wave 773 ci_sentinel_bridge tests."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave773_ci_sentinel_bridge as w773


def setup_function(_fn=None):
    w773.DATA.mkdir(parents=True, exist_ok=True)
    w773.STATE_FILE.write_text(json.dumps({
        "wave": 773, "name": "ci_sentinel_bridge",
        "scans": 0, "last_score": None, "last_posture": "unknown", "status": "test",
    }))


def test_contract():
    v = w773.coherence_vitals()
    assert v["wave"] == 773
    assert v["name"] == "ci_sentinel_bridge"
    assert "lab.ops.copilots.aegis" in w773.resonates_with()
    assert v["gate_policy"] == "organism_over_ghas_noise"


def test_scan_and_caption():
    setup_function()
    r = w773.handler({"action": "scan"})
    assert r["status"] == "scanned"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["posture"] in ("green", "amber", "red")
    assert 0.0 <= float(r["score"]) <= 1.0
    assert isinstance(r["checks"], list) and len(r["checks"]) >= 5
    cap = w773.handler({"action": "caption"})
    assert "sentinel" in cap["caption"]
    assert cap["audio"] is False
