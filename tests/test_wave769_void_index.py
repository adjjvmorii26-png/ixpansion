"""Wave 769 void_index — lab-gated organ tests."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave769_void_index as w769


def setup_function(_fn=None):
    w769.DATA.mkdir(parents=True, exist_ok=True)
    w769.STATE_FILE.write_text(json.dumps({
        "wave": 769, "name": "void_index",
        "entries": [], "lookups": 0, "status": "test",
    }))


def test_contract():
    v = w769.coherence_vitals()
    assert v["wave"] == 769
    assert v["name"] == "void_index"
    assert "wave763_silence_capacitor" in w769.resonates_with()
    assert callable(w769.handler)


def test_index_lookup_never_leaks_payload():
    setup_function()
    r = w769.handler({"action": "index", "text": "council hush that must stay unsaid"})
    assert r["status"] == "indexed"
    assert r["payload"] is None
    assert r["surface"] == "silence"
    key = r["key"]
    look = w769.handler({"action": "lookup", "key": key})
    assert look["status"] == "present"
    assert look["payload"] is None
    cap = w769.handler({"action": "caption"})
    assert cap["audio"] is False
    assert "void holds" in cap["caption"]
