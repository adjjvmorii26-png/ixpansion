import pytest
from omega_prime.nucleus.kernel.entanglement import EntanglementNetwork, BellState


class TestEntanglementNetwork:
    def test_entangle_pair(self):
        net = EntanglementNetwork(seed=42)
        result = net.entangle("alice", "bob")
        assert result["success"] is True

    def test_double_entangle_rejected(self):
        net = EntanglementNetwork(seed=42)
        net.entangle("a", "b")
        result = net.entangle("a", "c")
        assert result["success"] is False

    def test_measure_correlates_partner(self):
        net = EntanglementNetwork(seed=42)
        net.entangle("x", "y", bell_state=BellState.PHI_PLUS)
        result = net.measure("x", "spin", True)
        assert result is not None
        assert result.remote_value == True  # Same outcome (PHI_PLUS)

    def test_anticorrelated_measurement(self):
        net = EntanglementNetwork(seed=42)
        net.entangle("p", "q", bell_state=BellState.PSI_PLUS)
        result = net.measure("p", "spin", True)
        assert result is not None
        assert result.remote_value == False  # Opposite outcome

    def test_decoherence_over_measurements(self):
        net = EntanglementNetwork(seed=42)
        net.entangle("a", "b")
        measurements = 0
        while net.stats["active_pairs"] > 0 and measurements < 100:
            r = net.measure("a", "obs", 1.0)
            if r is None:
                break
            measurements += 1
        assert measurements < 100  # Should decohere before 100

    def test_natural_decay(self):
        net = EntanglementNetwork(seed=42)
        net.entangle("m", "n")
        dead = 0
        for _ in range(200):
            dead += net.tick_decay()
        assert dead >= 1

    def test_disentangle(self):
        net = EntanglementNetwork(seed=42)
        net.entangle("s", "t")
        assert net.disentangle("s") is True
        assert net.disentangle("s") is False
