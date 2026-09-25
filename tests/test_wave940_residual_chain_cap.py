"""Wave 940 residual_chain_cap tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave940_residual_chain_cap as w


def test_cap():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":940,"name":"residual_chain_cap","caps":0,"status":"test"}'
    )
    r = w.handler({"action": "cap"})
    assert r["status"] == "capped"
    assert r["audio"] is False
    assert r["payload"] is None
