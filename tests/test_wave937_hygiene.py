"""Wave 937 experiment_track_hygiene + atlas prune tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave937_experiment_track_hygiene as w937
import wave812_experiment_queue_atlas as w812


def test_937_scan():
    w937.DATA.mkdir(parents=True, exist_ok=True)
    w937.STATE_FILE.write_text(
        '{"wave":937,"name":"experiment_track_hygiene","scans":0,"status":"test"}'
    )
    r = w937.handler({"action": "scan"})
    assert r["status"] == "scanned"
    assert "report" in r
    assert r["audio"] is False


def test_812_prune_landed():
    w812.DATA.mkdir(parents=True, exist_ok=True)
    w812.STATE_FILE.write_text(
        '{"wave":812,"name":"experiment_queue_atlas","snapshots":0,"queue":'
        '[{"pr":1,"wave":906,"title":"x","track":"experiment"}],"status":"test"}'
    )
    r = w812.handler({"action": "prune_landed"})
    assert r["status"] == "pruned"
    waves = [x.get("wave") for x in (r.get("queue") or [])]
    assert 906 not in waves
