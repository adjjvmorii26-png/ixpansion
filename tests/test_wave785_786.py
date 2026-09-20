"""Waves 785–786 tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave785_silent_publish_orchestrator as w785
import wave786_echotide_caption_pace as w786


def test_785_publish_auto():
    w785.DATA.mkdir(parents=True, exist_ok=True)
    w785.STATE_FILE.write_text(
        '{"wave":785,"name":"silent_publish_orchestrator","runs":0,"last_outcome":null,"status":"test"}'
    )
    r = w785.handler({"action": "publish", "text": "council green hush", "auto_approve": True})
    assert r["status"] in ("published", "holding", "blocked", "denied")
    assert r["audio"] is False
    assert r["payload"] is None


def test_786_pace():
    w786.DATA.mkdir(parents=True, exist_ok=True)
    w786.STATE_FILE.write_text(
        '{"wave":786,"name":"echotide_caption_pace","paces":0,"status":"test"}'
    )
    r = w786.handler({"action": "pace", "frames": ["a", "b", "c"], "base_sec": 2})
    assert r["status"] == "paced"
    assert len(r["frames"]) == 3
    assert r["frames"][0]["t"] == 0
    assert r["audio"] is False
