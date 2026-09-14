"""Tests for Wave 651 — Self-Repair Engine."""
import pytest
from api.wave651_self_repair import handler, coherence_vitals, resonates_with
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave651_self_repair.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert r["scans"] == 0
    def test_scan_ok(self):
        r = handler({"action": "scan", "module": "api.wave648_ambient_sensor"})
        assert r["ok"] is True; assert r["scan"]["ok"] is True
    def test_scan_bad_module(self):
        r = handler({"action": "scan", "module": "api.no_such_module_xyz"})
        assert r["ok"] is True; assert r["scan"]["ok"] is False
    def test_repair(self):
        r = handler({"action": "repair", "module": "api.wave651_self_repair"})
        assert r["ok"] is True; assert r["repair"]["status"] == "healed"
    def test_report(self):
        handler({"action": "scan", "module": "api.wave648_ambient_sensor"})
        r = handler({"action": "report"}); assert r["ok"] is True; assert r["total_scans"] == 1
    def test_unknown(self):
        r = handler({"action": "foo"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 651
class TestResonates:
    def test_list(self):
        assert "wave650_auto_optimizer" in resonates_with()
