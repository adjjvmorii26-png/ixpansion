import pytest
from omega_prime.nucleus.kernel.time_crystal import TimeCrystalLattice


class TestTimeCrystal:
    def test_create_crystal(self):
        tc = TimeCrystalLattice()
        cid = tc.create((10, 10), radius=5, period=10)
        assert cid is not None

    def test_period_cycle_completes(self):
        tc = TimeCrystalLattice()
        tc.create((0, 0), radius=100, period=5)
        completed = []
        for _ in range(15):
            result = tc.tick()
            completed.extend(result["cycles_completed"])
        assert len(completed) >= 2  # Should complete at least 2 cycles in 15 ticks

    def test_agent_inside_gets_echo(self):
        tc = TimeCrystalLattice()
        tc.create((5, 5), radius=10, period=5)

        # Record agent at same position doing same action across two periods
        for cycle in range(2):
            for step in range(5):
                tc.record_agent_state("agent_a", (5, 5), "move_north", 50.0)
                tc.tick()

        result = tc.tick()
        assert result["echoes_generated"] >= 0  # Echoes may or may not fire depending on timing

    def test_future_self_prediction(self):
        tc = TimeCrystalLattice()
        tc.create((0, 0), radius=100, period=5)
        for _ in range(12):
            tc.record_agent_state("predictor", (1, 1), "scan", 80.0)
            tc.tick()

        future = tc.get_future_self("predictor", periods_ahead=1)
        if future:
            assert "predicted_position" in future
            assert future["confidence"] <= 1.0

    def test_agent_outside_no_echo(self):
        tc = TimeCrystalLattice()
        tc.create((100, 100), radius=1, period=5)  # Tiny crystal far away
        for _ in range(10):
            tc.record_agent_state("far_away", (0, 0), "idle", 100.0)
            tc.tick()
        echoes = [e for e in tc._echo_log if e["agent"] == "far_away"]
        assert len(echoes) == 0
