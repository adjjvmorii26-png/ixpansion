"""Waves 811–813 tests."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave811_triad_discovery_bridge as w811
import wave812_experiment_queue_atlas as w812
import wave813_null_evidence_registry as w813


def test_811_bridge():
    w811.DATA.mkdir(parents=True, exist_ok=True)
    w811.STATE_FILE.write_text(
        '{"wave":811,"name":"triad_discovery_bridge","bridges":0,"status":"test"}'
    )
    r = w811.handler({"action": "bridge"})
    assert r["status"] in ("bridged", "waiting")
    assert r["audio"] is False


def test_812_rank():
    w812.DATA.mkdir(parents=True, exist_ok=True)
    w812.STATE_FILE.write_text(
        json.dumps({
            "wave": 812,
            "name": "experiment_queue_atlas",
            "snapshots": 0,
            "queue": [
                {"pr": 172, "wave": 900, "title": "synchronicity_engine", "track": "experiment"},
                {"pr": 176, "wave": 904, "title": "evidence_ledger", "track": "experiment"},
            ],
            "status": "test",
        })
    )
    r = w812.handler({"action": "rank"})
    assert r["next_merge_candidate"]["wave"] == 900


def test_813_null():
    w813.DATA.mkdir(parents=True, exist_ok=True)
    w813.STATE_FILE.write_text(
        '{"wave":813,"name":"null_evidence_registry","entries":[],"status":"test"}'
    )
    r = w813.handler({"action": "record", "hypothesis": "h", "note": "null"})
    assert r["status"] == "recorded"
