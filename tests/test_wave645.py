"""Tests for Wave 645 — Communication Protocol."""
import pytest
from api.wave645_communication import handler, coherence_vitals, resonates_with
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave645_communication.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert "v1" in r["protocols"]
    def test_send(self):
        r = handler({"action": "send", "sender": "alpha", "receiver": "beta", "type": "info", "body": "hello"})
        assert r["ok"] is True; assert r["status"] == "delivered"
    def test_inbox(self):
        handler({"action": "send", "sender": "alpha", "receiver": "beta", "type": "info", "body": "hi"})
        r = handler({"action": "inbox", "receiver": "beta"})
        assert r["ok"] is True; assert r["count"] == 1
    def test_inbox_empty(self):
        r = handler({"action": "inbox", "receiver": "ghost"}); assert r["count"] == 0
    def test_unknown(self):
        r = handler({"action": "xyz"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 645
class TestResonates:
    def test_list(self):
        assert "wave638_symbiosis_protocol" in resonates_with()
