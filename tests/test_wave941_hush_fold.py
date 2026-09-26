"""Wave 941 hush_fold tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave941_hush_fold as w


def test_fold():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":941,"name":"hush_fold","folds":0,"token":"","status":"test"}'
    )
    r = w.handler({"action": "fold", "caption": "residual chain capped · empty"})
    assert r["status"] == "folded"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert len(r["token"]) == 16


def test_vitals_and_resonance():
    v = w.coherence_vitals()
    assert v["wave"] == 941
    assert v["ok"] is True
    assert "wave940_residual_chain_cap" in w.resonates_with()
