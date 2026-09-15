"""Tests for zen_session — the meditation engine."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import zen_session as zs


def test_coherence_vitals():
    cv = zs.coherence_vitals()
    assert cv["wave"] == 700 and cv["ok"] is True


def test_open_session():
    result = zs.handler({"action": "open", "depth": 3})
    assert result["status"] == "meditated" and result["depth"] == 3
    assert len(result["insights"]) == 3


def test_reflect():
    r = zs.handler({"action": "open", "depth": 2})
    reflected = zs.handler({"action": "reflect", "session_id": r["session_id"]})
    assert reflected["status"] == "reflected"


def test_silence():
    s = zs.handler({"action": "silence", "minutes": 5})
    assert s["status"] == "silent" and s["total_silence"] >= 5


def test_status():
    st = zs.handler({"action": "status"})
    assert st["status"] == "active" and st["wave"] == 700
