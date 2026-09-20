"""Waves 783–784 tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave783_hitl_publish_gate as w783
import wave784_glass_orchard_compress as w784


def test_783_hold_approve_deny_risk():
    w783.DATA.mkdir(parents=True, exist_ok=True)
    w783.STATE_FILE.write_text(
        '{"wave":783,"name":"hitl_publish_gate","pending":[],"decisions":0,"status":"test"}'
    )
    h = w783.handler({"action": "submit", "label": "cap"})
    assert h["status"] == "holding"
    a = w783.handler({"action": "approve", "id": h["id"]})
    assert a["status"] == "approved"
    d = w783.handler({"action": "submit", "label": "bad", "risk_score": 0.9})
    assert d["status"] == "denied"
    assert d["audio"] is False


def test_784_compress():
    w784.DATA.mkdir(parents=True, exist_ok=True)
    w784.STATE_FILE.write_text(
        '{"wave":784,"name":"glass_orchard_compress","crystals":[],"status":"test"}'
    )
    r = w784.handler({"action": "compress", "text": "hello void hush"})
    assert r["status"] == "compressed"
    assert r["payload"] is None
    assert r["crystal"]["digest"]
    assert r["audio"] is False
