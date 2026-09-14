"""Tests for Wave 638 — Symbiosis Protocol."""
import pytest
from api.wave638_symbiosis_protocol import handler, coherence_vitals, resonates_with

@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    state = Path("data/wave638_symbiosis_protocol.json")
    if state.exists():
        state.unlink()
    yield
    if state.exists():
        state.unlink()

class TestHandler:
    def test_status(self):
        r = handler({})
        assert r["ok"] is True
        assert r["protocol_version"] == "1.0.0"
        assert r["total_partners"] == 0

    def test_handshake(self):
        r = handler({"action": "handshake", "partner_id": "nexus-observatory", "platform": "github"})
        assert r["ok"] is True
        assert r["state"] == "received"

    def test_engage(self):
        r = handler({"action": "engage", "partner_id": "nexus-observatory", "capabilities": ["mesh", "oracle"]})
        assert r["ok"] is True
        assert r["status"] == "joint"
        assert r["partner"] == "nexus-observatory"

    def test_resonate(self):
        handler({"action": "engage", "partner_id": "nexus-observatory"})
        r = handler({"action": "resonate", "a": "ixpansion", "b": "nexus-observatory", "signal_strength": 0.8})
        assert r["ok"] is True
        assert r["resonance"]["score"] > 0

    def test_share(self):
        handler({"action": "engage", "partner_id": "nexus-observatory"})
        r = handler({"action": "share", "partner_id": "nexus-observatory", "resource": "dashboards", "amount": 3})
        assert r["ok"] is True
        assert r["total"] == 3

    def test_relations(self):
        r = handler({"action": "relations"})
        assert r["ok"] is True
        assert "resonance_scores" in r

    def test_partner_count(self):
        handler({"action": "engage", "partner_id": "p1"})
        handler({"action": "engage", "partner_id": "p2"})
        r = handler({"action": "status"})
        assert r["total_partners"] == 2

    def test_unknown_action(self):
        r = handler({"action": "nope"})
        assert r["ok"] is False

class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals()
        assert v["wave"] == 638
        assert "partners" in v

class TestResonates:
    def test_list(self):
        r = resonates_with()
        assert "wave637_meta_regulation" in r
        assert "omnirouter" in r
