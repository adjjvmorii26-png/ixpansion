"""Tests for big_pickle_gateway — unified API."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import big_pickle_gateway as gw


def test_coherence_vitals():
    cv = gw.coherence_vitals()
    assert cv["wave"] == 700 and cv["ok"] is True


def test_meditate():
    result = gw.handler({"action": "meditate", "state": {"test": True}, "depth": 2})
    assert result["status"] == "meditated"
    assert "insights" in result and len(result["insights"]) > 0


def test_full_report():
    report = gw.handler({"action": "full_report"})
    assert report["status"] == "report"
    assert "pickle_jar" in report and "zen_session" in report


def test_status():
    st = gw.handler({"action": "status"})
    assert st["status"] == "active" and st["wave"] == 700
