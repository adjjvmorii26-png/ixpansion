import pytest
from omega_prime.sandbox.modules.pheromone_field import PheromoneField


class TestPheromoneField:
    def test_deposit_and_sense(self):
        field = PheromoneField()
        field.deposit(5, 5, "sentinel", 1.0)
        reading = field.sense(5, 5, "sentinel")
        assert reading > 0

    def test_species_isolation(self):
        field = PheromoneField()
        field.deposit(5, 5, "sentinel", 1.0)
        assert field.sense(5, 5, "wanderer") == 0.0
        assert field.sense(5, 5, "sentinel") > 0

    def test_evaporation_reduces(self):
        field = PheromoneField()
        field.deposit(3, 3, "scout", 1.0)
        before = field.sense(3, 3, "scout")
        for _ in range(50):
            field.evaporate(rate=0.1)
        after = field.sense(3, 3, "scout")
        assert after < before

    def test_attract_to_returns_direction(self):
        field = PheromoneField(width=20, height=20)
        field.deposit(5, 5, "scout", 1.0)
        target = field.attract_to(3, 3, "scout", sensitivity=0.01)
        assert target is not None

    def test_attract_to_no_signal(self):
        field = PheromoneField()
        result = field.attract_to(10, 10, "ghost_species")
        assert result is None

    def test_density_map(self):
        field = PheromoneField()
        field.deposit(1, 1, "alpha", 0.8)
        field.deposit(2, 2, "beta", 0.6)
        density = field.density_map
        assert "alpha" in density and "beta" in density

    def test_clamped_deposits(self):
        field = PheromoneField(width=4, height=4)
        field.deposit(-100, -100, "s", 1.0)  # Should clamp to (0,0)
        assert field.sense(0, 0, "s") > 0
