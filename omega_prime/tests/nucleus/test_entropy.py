import pytest
from omega_prime.nucleus.kernel.entropy import (
    EntropyLedger, EntropyGovernor, classify_entropy,
)


class TestEntropyLedger:
    def test_spend_reduces_level(self):
        ledger = EntropyLedger(capacity=100)
        assert ledger.spend(10) is True
        assert ledger.level == 90

    def test_lockout_on_depletion(self):
        ledger = EntropyLedger(capacity=5)
        ledger.spend(4)
        assert not ledger.is_locked
        ledger.spend(2)  # Would go negative
        assert ledger.is_locked

    def test_lockout_blocks_spending(self):
        ledger = EntropyLedger(capacity=1)
        ledger.spend(1)
        assert ledger.spend(0.5) is False

    def test_regeneration_recovers(self):
        ledger = EntropyLedger(capacity=100, regeneration_rate=10)
        ledger.spend(50)
        for _ in range(6):
            ledger.regenerate()
        assert ledger.level == 100

    def test_pressure_calculation(self):
        ledger = EntropyLedger(capacity=100)
        ledger.level = 20
        assert ledger.pressure == pytest.approx(0.8)


class TestEntropyClassification:
    def test_known_action_cost(self):
        assert classify_entropy({"intent": "move"}) == 1.0
        assert classify_entropy({"intent": "attack"}) == 12.0
        assert classify_entropy({"intent": "idle"}) == 0.0

    def test_unknown_action_has_cost(self):
        cost = classify_entropy({"intent": "unknown_thing"})
        assert cost > 0


class TestGovernor:
    def test_enroll_and_authorize(self):
        gov = EntropyGovernor()
        gov.enroll("agent-1")
        allowed, cost = gov.authorize("agent-1", {"intent": "move"})
        assert allowed is True and cost == 1.0

    def test_tick_report(self):
        gov = EntropyGovernor()
        gov.enroll("a1")
        report = gov.tick()
        assert "a1" in report
        assert "level" in report["a1"]
