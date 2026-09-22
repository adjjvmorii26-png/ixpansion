"""Waves 803–805 tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave803_margin_publish_gate as w803
import wave804_dawn_weather_sync as w804
import wave805_null_choir_counter as w805


def test_803_gate():
    w803.DATA.mkdir(parents=True, exist_ok=True)
    w803.STATE_FILE.write_text(
        '{"wave":803,"name":"margin_publish_gate","gates":0,"status":"test"}'
    )
    r = w803.handler({"action": "gate", "text": "hush"})
    assert r["status"] in ("allowed", "holding", "denied")
    assert r["audio"] is False


def test_804_sync():
    w804.DATA.mkdir(parents=True, exist_ok=True)
    w804.STATE_FILE.write_text(
        '{"wave":804,"name":"dawn_weather_sync","syncs":0,"status":"test"}'
    )
    r = w804.handler({"action": "sync", "hour": 6, "activity": 0.2})
    assert r["status"] == "synced"
    assert r["vector"]


def test_805_tick():
    w805.DATA.mkdir(parents=True, exist_ok=True)
    w805.STATE_FILE.write_text(
        '{"wave":805,"name":"null_choir_counter","streak":0,"max_streak":0,"events":0,"status":"test"}'
    )
    a = w805.handler({"action": "tick", "silent": True})
    assert a["streak"] == 1
    b = w805.handler({"action": "tick", "silent": True})
    assert b["streak"] == 2
    c = w805.handler({"action": "tick", "silent": False})
    assert c["streak"] == 0
