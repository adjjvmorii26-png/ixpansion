import pytest
from omega_fractal_engine.nucleus.kernel.entropy_regulator import EntropyRegulator


class TestEntropyRegulator:
    def test_initial_state(self):
        reg = EntropyRegulator()
        assert 0.0 <= reg.current_entropy <= 1.0

    def test_regulate_moves_toward_target(self):
        reg = EntropyRegulator(target_entropy=0.9)
        reg.current_entropy = 0.3
        for _ in range(100):
            reg.regulate()
        assert reg.current_entropy > 0.5

    def test_regimes(self):
        reg = EntropyRegulator()
        reg.current_entropy = 0.05
        assert reg.regime == "crystalline"
        reg.current_entropy = 0.95
        assert reg.regime == "inferno"

    def test_chaos_budget(self):
        reg = EntropyRegulator()
        reg.current_entropy = 0.8
        assert reg.chaos_budget == pytest.approx(0.2)

    def test_set_target_clamps(self):
        reg = EntropyRegulator()
        reg.set_target(-5)
        assert reg.target_entropy == 0.0
        reg.set_target(99)
        assert reg.target_entropy == 1.0
