"""Waves 935–936 tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave935_verification_null_bridge as w935
import wave936_skillforge_verify_fuse as w936


def test_935():
    w935.DATA.mkdir(parents=True, exist_ok=True)
    w935.STATE_FILE.write_text(
        '{"wave":935,"name":"verification_null_bridge","bridges":0,"status":"test"}'
    )
    r = w935.handler({"action": "bridge", "gap": "missing proof"})
    assert r["status"] == "bridged"
    assert r["audio"] is False


def test_936():
    w936.DATA.mkdir(parents=True, exist_ok=True)
    w936.STATE_FILE.write_text(
        '{"wave":936,"name":"skillforge_verify_fuse","fuses":0,"status":"test"}'
    )
    r = w936.handler({"action": "fuse", "skill": "skillforge", "decision": "hold"})
    assert r["status"] == "fused"
