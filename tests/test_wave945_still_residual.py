"""Wave 945 still_residual_bridge tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave945_still_residual_bridge as w


def test_bridge():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":945,"name":"still_residual_bridge","bridges":0,"status":"test"}'
    )
    r = w.handler({"action": "bridge"})
    assert r["status"] == "bridged"
    assert r["audio"] is False
    assert r["payload"] is None
