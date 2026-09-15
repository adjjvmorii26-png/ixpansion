"""Tests for Wave 663 — Resonance Ledger."""
import pytest
from api.wave663_resonance_ledger import handler, coherence_vitals, resonates_with
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave663_resonance_ledger.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert r["accounts"] == 0
    def test_mint(self):
        r = handler({"action": "mint", "account": "cortex", "amount": 20.0})
        assert r["ok"] is True; assert r["balance"] == 20.0
    def test_transfer(self):
        handler({"action": "mint", "account": "a", "amount": 10.0})
        r = handler({"action": "transfer", "from": "a", "to": "b", "amount": 4.0})
        assert r["ok"] is True; assert r["balances"]["from"] == 6.0; assert r["balances"]["to"] == 4.0
    def test_transfer_insufficient(self):
        r = handler({"action": "transfer", "from": "empty", "to": "b", "amount": 5.0})
        assert r["ok"] is False
    def test_balance(self):
        handler({"action": "mint", "account": "x", "amount": 7.0})
        r = handler({"action": "balance", "account": "x"}); assert r["ok"] is True; assert r["balance"] == 7.0
    def test_ledger(self):
        r = handler({"action": "ledger"}); assert r["ok"] is True
    def test_unknown(self):
        r = handler({"action": "foo"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 663
class TestResonates:
    def test_list(self):
        assert "wave665_mycelial_network" in resonates_with()
