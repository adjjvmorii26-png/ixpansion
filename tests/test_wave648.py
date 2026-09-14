"""Tests for Wave 648 — Ambient Sensor."""
import pytest
from api.wave648_ambient_sensor import handler, coherence_vitals, resonates_with
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave648_ambient_sensor.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert r["signals"] == 0
    def test_sense(self):
        r = handler({"action": "sense", "channel": "cortex", "value": 2.0})
        assert r["ok"] is True; assert r["signal"]["value"] == 2.0
    def test_channel(self):
        handler({"action": "sense", "channel": "cortex", "value": 2.0})
        r = handler({"action": "channel", "channel": "cortex"})
        assert r["ok"] is True; assert r["signals"] == 1; assert r["mean"] == 2.0
    def test_summary(self):
        handler({"action": "sense", "channel": "cortex"})
        r = handler({"action": "summary"}); assert r["ok"] is True; assert r["fresh"] == 1
    def test_unknown(self):
        r = handler({"action": "foo"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 648
class TestResonates:
    def test_list(self):
        assert "wave649_pattern_predictor" in resonates_with()
