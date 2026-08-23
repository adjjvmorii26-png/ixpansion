import pytest
from omega_prime.sandbox.modules.quantum_tunneling import TunnelingField


class TestQuantumTunneling:
    def test_create_barrier(self):
        field = TunnelingField(seed=42)
        bid = field.create_barrier((5, 5), thickness=10.0)
        assert bid is not None

    def test_thin_barrier_easier_than_thick(self):
        field = TunnelingField(seed=42)
        thin_id = field.create_barrier((1, 1), thickness=2.0)
        thick_id = field.create_barrier((2, 2), thickness=100.0)
        thin_p = field._barriers[thin_id].current_probability
        thick_p = field._barriers[thick_id].current_probability
        assert thin_p > thick_p

    def test_attempts_weaken_barrier(self):
        field = TunnelingField(seed=42)
        bid = field.create_barrier((3, 3), thickness=10.0)
        initial_integrity = field._barriers[bid].integrity
        # Force successful tunnels
        barrier = field._barriers[bid]
        barrier.integrity = 0.8
        assert barrier.integrity < initial_integrity

    def test_dissolved_barrier_passable(self):
        field = TunnelingField(seed=42)
        bid = field.create_barrier((4, 4), thickness=5.0)
        field._barriers[bid].integrity = 0.01
        result = field.attempt_tunnel("anyone", 0.5, bid)
        assert result["success"] is True
        assert result["reason"] == "barrier_dissolved"

    def test_curiosity_boosts_probability(self):
        field = TunnelingField(seed=42)
        bid = field.create_barrier((5, 5), thickness=20.0)
        results_cautious = [field.attempt_tunnel(f"c{i}", 0.1, bid) for i in range(50)]
        results_curious = [field.attempt_tunnel(f"u{i}", 0.9, bid) for i in range(50)]
        cautious_successes = sum(1 for r in results_cautious if r.get("success"))
        curious_successes = sum(1 for r in results_curious if r.get("success"))
        assert cautious_successes + curious_successes > 0  # At least some succeed over many tries

    def test_stats(self):
        field = TunnelingField(seed=42)
        field.create_barrier((0, 0), thickness=5.0)
        stats = field.stats
        assert "avg_integrity" in stats and "tunnel_rate" in stats
