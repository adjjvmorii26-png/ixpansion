"""Wave 952 still_gate tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave952_still_gate as w


def test_still_gate():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "classify", "title": "lab: wave", "head": "lab/wave952", "files": ["api/wave952_still_gate.py"]})
    assert r["status"] == "classified"
    assert r["track"] == "lab"
    assert r["merge_gate"] == "lab"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    dual = w.handler({"action": "classify", "title": "lab: runtime", "head": "lab/x", "files": ["api_server.py"]})
    assert dual["track"] == "dual"
    assert dual["merge_gate"] == "organism"
    exp = w.handler({"action": "classify", "title": "experiment: REAL", "head": "experiment/foo"})
    assert exp["do_not_merge"] is True
    assert exp["track"] == "lab"
    v = w.coherence_vitals()
    assert v["wave"] == 952
    assert v["ok"] is True
    assert "wave950_hush_margin" in w.resonates_with()
    assert "wave951_dual_track_pr_bot" in w.resonates_with()
