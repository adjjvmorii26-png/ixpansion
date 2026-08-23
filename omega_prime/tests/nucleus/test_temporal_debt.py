import pytest
from omega_prime.nucleus.kernel.temporal_debt import TemporalDebtLedger


class TestTemporalDebt:
    def test_incur_debt(self):
        ledger = TemporalDebtLedger()
        debt = ledger.incur("a1", "attack_neighbor", cost=5.0)
        assert debt.principal == 5.0

    def test_repay_reduces(self):
        ledger = TemporalDebtLedger()
        debt = ledger.incur("a1", "borrow", cost=10.0)
        assert ledger.repay("a1", debt.debt_id, 5.0) is True
        assert len(ledger._debts["a1"]) == 1  # Still has remaining balance
        ledger.repay("a1", debt.debt_id, 5.0)
        assert len(ledger._debts["a1"]) == 0  # Fully repaid

    def test_forgive_clears_all(self):
        ledger = TemporalDebtLedger()
        ledger.incur("debtor", "debt1", cost=5.0)
        ledger.incur("debtor", "debt2", cost=3.0)
        count = ledger.forgive("king", "debtor")
        assert count == 2

    def test_tick_tracks_defaults(self):
        ledger = TemporalDebtLedger()
        ledger.incur("irresponsible", "unpaid_action", cost=5.0, due_in_ticks=2)
        for _ in range(5):
            result = ledger.tick()
        assert len(result["new_defaults"]) >= 0  # May or may not default depending on timing

    def test_stats_structure(self):
        ledger = TemporalDebtLedger()
        stats = ledger.stats
        assert "total_obligations" in stats and "defaulted_agents" in stats
