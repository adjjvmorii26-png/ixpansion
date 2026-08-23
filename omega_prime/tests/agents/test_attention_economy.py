import pytest
from omega_prime.agents.attention_economy import AttentionEconomy, MAX_ATTENTION


class TestAttentionEconomy:
    def test_enroll_and_observe(self):
        eco = AttentionEconomy()
        eco.enroll("observer")
        eco.enroll("target")
        result = eco.observe("observer", "target")
        assert result["status"] == "ok"
        assert result["observer_balance"] < result["target_balance"]

    def test_bankrupt_observer_blocked(self):
        eco = AttentionEconomy()
        eco.enroll("broke", starting_balance=0.0)
        eco.enroll("rich")
        result = eco.observe("broke", "rich")
        assert result["status"] == "observer_bankrupt"

    def test_visible_action_earns(self):
        eco = AttentionEconomy()
        eco.enroll("performer", starting_balance=5.0)
        reward = eco.perform_visible_action("performer", "attack")
        assert reward > 0

    def test_transfer_between_agents(self):
        eco = AttentionEconomy()
        eco.enroll("giver", starting_balance=10.0)
        eco.enroll("receiver", starting_balance=0.0)
        assert eco.transfer("giver", "receiver", 5.0) is True
        assert eco.transfer("giver", "receiver", 100.0) is False  # Insufficient

    def test_gini_coefficient_range(self):
        eco = AttentionEconomy()
        for i in range(10):
            eco.enroll(f"a{i}", starting_balance=float(i))
        stats = eco.stats
        assert 0.0 <= stats["gini_coefficient"] <= 1.0

    def test_rich_list_sorted(self):
        eco = AttentionEconomy()
        for i in range(15):
            eco.enroll(f"a{i}", starting_balance=float(i))
        rich = eco.rich_list
        balances = [r["balance"] for r in rich]
        assert balances == sorted(balances, reverse=True)

    def test_reset_tick_clears_counters(self):
        eco = AttentionEconomy()
        eco.enroll("a"); eco.enroll("b")
        eco.observe("a", "b")
        eco.reset_tick()
        stats = eco.stats
        assert stats["agents"] == 2
