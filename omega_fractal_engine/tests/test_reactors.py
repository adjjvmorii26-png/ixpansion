import pytest
from omega_fractal_engine.reactors.chaos_reactor import ChaosReactor
from omega_fractal_engine.reactors.order_reactor import OrderReactor
from omega_fractal_engine.reactors.fusion_reactor import FusionReactor
from omega_fractal_engine.reactors.inversion_reactor import InversionReactor


class TestChaos:
    def test_inject_perturbs(self):
        reactor = ChaosReactor(seed=42)
        state = {"x": 10.0, "y": 20.0}
        result = reactor.inject(state, magnitude=5.0)
        # Values should have changed
        assert result["x"] != 10.0 or result["y"] != 20.0

    def test_injection_count(self):
        reactor = ChaosReactor(seed=42)
        state = {"a": 1.0, "b": 2.0}
        reactor.inject(state)
        assert reactor.total_injections >= 1


class TestOrder:
    def test_normalize_snaps(self):
        reactor = OrderReactor()
        state = {"x": 3.01}  # Very close to 3.0
        result = reactor.normalize(state)
        assert result["x"] == 3.0

    def test_symmetry_mirrors(self):
        reactor = OrderReactor()
        positions = [(1.0, 2.0)]
        mirrored = reactor.enforce_symmetry(positions)
        assert (-1.0, -2.0) in mirrored


class TestFusion:
    def test_fuse_equal_bias(self):
        reactor = FusionReactor()
        a = {"aggression": 0.2, "speed": 0.8}
        b = {"aggression": 0.8, "speed": 0.4}
        fused = reactor.fuse(a, b, bias=0.5)
        assert fused["aggression"] == pytest.approx(0.5)
        assert fused["speed"] == pytest.approx(0.6)

    def test_full_bias_b(self):
        reactor = FusionReactor()
        a = {"x": 0.0}
        b = {"x": 1.0}
        fused = reactor.fuse(a, b, bias=1.0)
        assert fused["x"] == pytest.approx(1.0)


class TestInversion:
    def test_invert_booleans(self):
        inv = InversionReactor()
        result = inv.invert({"flag": True})
        assert result["flag"] is False

    def test_invert_numbers(self):
        inv = InversionReactor()
        result = inv.invert({"x": 42})
        assert result["x"] == -42

    def test_invert_string(self):
        inv = InversionReactor()
        result = inv.invert({"msg": "hello"})
        assert result["msg"] == "olleh"
