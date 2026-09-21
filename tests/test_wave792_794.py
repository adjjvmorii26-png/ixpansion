"""Waves 792–794 tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave792_weather_route_bridge as w792
import wave793_void_orchard_bridge as w793
import wave794_organ_debt_auditor as w794


def test_792_bridge():
    w792.DATA.mkdir(parents=True, exist_ok=True)
    w792.STATE_FILE.write_text(
        '{"wave":792,"name":"weather_route_bridge","bridges":0,"status":"test"}'
    )
    r = w792.handler({"action": "bridge", "text": "aaaaaaaa", "activity": 0.1})
    assert r["status"] == "bridged"
    assert r["audio"] is False


def test_793_ingest():
    w793.DATA.mkdir(parents=True, exist_ok=True)
    w793.STATE_FILE.write_text(
        '{"wave":793,"name":"void_orchard_bridge","keys":[],"status":"test"}'
    )
    r = w793.handler({"action": "ingest", "text": "void hush"})
    assert r["status"] == "ingested"
    assert r["payload"] is None


def test_794_audit():
    w794.DATA.mkdir(parents=True, exist_ok=True)
    w794.STATE_FILE.write_text(
        '{"wave":794,"name":"organ_debt_auditor","audits":0,"status":"test"}'
    )
    r = w794.handler({"action": "audit"})
    assert r["status"] == "audited"
    assert r["scanned"] >= 1
    assert isinstance(r["debt"], int)
