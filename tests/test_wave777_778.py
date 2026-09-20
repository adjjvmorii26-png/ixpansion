"""Waves 777–778 tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave777_ledger_sync_bridge as w777
import wave778_antimeme_caption_guard as w778


def test_777_ingest():
    w777.DATA.mkdir(parents=True, exist_ok=True)
    w777.STATE_FILE.write_text(
        '{"wave":777,"name":"ledger_sync_bridge","entries":[],"syncs":0,"status":"test"}'
    )
    assert w777.coherence_vitals()["wave"] == 777
    r = w777.handler({"action": "ingest"})
    assert r["status"] == "synced"
    assert r["audio"] is False
    idx = w777.handler({"action": "index"})
    assert idx["count"] >= 1


def test_778_scan():
    w778.DATA.mkdir(parents=True, exist_ok=True)
    w778.STATE_FILE.write_text(
        '{"wave":778,"name":"antimeme_caption_guard","scans":0,"blocked":0,"status":"test"}'
    )
    safe = w778.handler({"action": "scan", "text": "council green · hush"})
    assert safe["verdict"] == "pass"
    assert safe["audio"] is False
    risky = w778.handler(
        {"action": "scan", "text": "password secret token api_key https://evil.example/x"}
    )
    assert risky["verdict"] in ("trim", "block")
    assert risky["score"] >= 0.2
