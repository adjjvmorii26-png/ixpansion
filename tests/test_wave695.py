"""Wave 695 Memory Palace Reanimation tests."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave695_memory_palace_reanimation as w


def test_coherence_vitals():
    cv = w.coherence_vitals()
    assert cv["wave"] == 695 and cv["module"] == "wave695_memory_palace_reanimation"
    assert cv["ok"] is True


def test_resonates_with():
    r = w.resonates_with()
    assert len(r) > 0


def test_store_and_recall():
    s = w.handler({"action": "store_memory", "memory_id": "m1", "content": "the first secret", "room": "atrium"})
    assert s["status"] == "stored"
    r = w.handler({"action": "recall", "memory_id": "m1"})
    assert r["status"] == "recalled" and r["content"] == "the first secret"
    st = w.handler({"action": "status"})
    assert st["memories_stored"] == 1 and st["rooms"] == 1


def test_traverse():
    t = w.handler({"action": "traverse", "room": "atrium"})
    assert t["status"] == "traversed" and t["room"] == "atrium"


def test_status():
    st = w.handler({"action": "status"})
    assert st["status"] == "active" and st["wave"] == 695
