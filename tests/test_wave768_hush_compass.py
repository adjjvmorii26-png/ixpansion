"""Wave 768 hush_compass — lab-gated organ tests."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave768_hush_compass as w768


def setup_function(_fn=None):
    if w768.DATA_FILE.exists():
        w768.DATA_FILE.write_text(json.dumps({
            "wave": 768, "name": "hush_compass",
            "bearings": [], "memory": [], "captions": [], "status": "test",
        }))


def test_contract():
    v = w768.coherence_vitals()
    assert v["wave"] == 768
    assert v["name"] == "hush_compass"
    assert "silence_capacitor" in w768.resonates_with()
    assert callable(w768.handler)


def test_bear_listen_caption_compress():
    setup_function()
    born = w768.handler({"action": "bear", "subject": "council", "bearing": "withhold"})
    assert born.get("born") is True
    # charge starts at 0.2 < 0.35 so compress would swallow it; reinforce first
    w768.handler({"action": "bear", "subject": "council", "bearing": "withhold"})
    heard = w768.handler({"action": "listen", "subject": "council"})
    assert heard["discharged"] is False
    assert heard["count"] == 1
    cap = w768.handler({"action": "caption", "subject": "council", "text": "hush holds council"})
    assert cap["discharged"] is True
    assert cap["surface"] == "silence"
    # leftover low charge compresses into memory
    packed = w768.handler({"action": "compress"})
    assert "council" in packed["compressed"]
    status = w768.handler({"action": "status"})
    assert status["surface"] == "silence"
    assert status["memory_cells"] >= 1
