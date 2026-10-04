"""Wave 951 experiment_x1000 tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave951_experiment_x1000 as w


def test_batch_1000():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text('{"wave":951,"name":"experiment_x1000","runs":0,"status":"test"}')
    r = w.handler({"action": "run", "batch": 1000, "keep": 5})
    assert r["status"] == "accelerated"
    assert r["result"]["batch"] == 1000
    assert len(r["result"]["survivors"]) == 5
    assert r["audio"] is False
    assert r["result"]["elapsed_ms"] < 5000


def test_encode_stable():
    assert w.encode_hex("REAL") == w.encode_hex("REAL")
