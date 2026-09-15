"""Wave 697 Neural Syntax Bridge tests."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave697_neural_syntax_bridge as w


def test_coherence_vitals():
    cv = w.coherence_vitals()
    assert cv["wave"] == 697 and cv["ok"] is True


def test_resonates_with():
    r = w.resonates_with()
    assert len(r) > 0


def test_translate():
    t = w.handler({"action": "translate", "content": "hello organism", "source_lang": "org_internal", "target_lang": "json"})
    assert t["status"] == "translated" and t["quality"] > 0.0
    st = w.handler({"action": "status"})
    assert st["bridge_count"] == 1


def test_bridge():
    t = w.handler({"action": "translate", "content": "test"})
    bid = t["bridge_id"]
    b = w.handler({"action": "bridge", "bridge_id": bid})
    assert b["status"] == "bridge"


def test_syntax():
    s = w.handler({"action": "syntax"})
    assert s["status"] == "syntax" and len(s["rules"]) > 0


def test_status():
    st = w.handler({"action": "status"})
    assert st["status"] == "active" and st["wave"] == 697
