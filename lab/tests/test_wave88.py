from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

class TestConsciousnessField:
    def test_simulate(self):
        from lab.consciousness_field import ConsciousnessField
        f = ConsciousnessField(42, grid_size=10)
        f.add_well(5, 5, 1.0)
        r = f.simulate(ticks=10)
        assert r["ticks"] == 10; assert r["awareness"] >= 0
    def test_demo(self):
        from lab.consciousness_field import demo
        r = demo(); assert r["report"]["wells"] == 8

class TestTimeCrystalOscillator:
    def test_pulse(self):
        from lab.time_crystal_oscillator import TimeCrystal
        tc = TimeCrystal(period=4, seed=42)
        r = tc.pulse({"a": {"energy": 0.8}})
        assert "phase" in r
    def test_simulate(self):
        from lab.time_crystal_oscillator import TimeCrystal
        tc = TimeCrystal(period=4, seed=42)
        r = tc.simulate(ticks=20)
        assert r["ticks"] == 20; assert r["echoes"] >= 0
    def test_demo(self):
        from lab.time_crystal_oscillator import demo
        r = demo(); assert r["report"]["period"] == 6

class TestQuantumEntanglementNetwork:
    def test_entangle(self):
        from lab.quantum_entanglement_network import QuantumEntanglementNetwork
        n = QuantumEntanglementNetwork(42)
        n.add_node("a", "lab"); n.add_node("b", "api")
        e = n.entangle("a", "b")
        assert "strength" in e; assert e["pair"] == ("a", "b")
    def test_demo(self):
        from lab.quantum_entanglement_network import demo
        r = demo(); assert r["nodes"] > 0

class TestGravitationalLens:
    def test_trace(self):
        from lab.gravitational_lens import GravitationalLens
        l = GravitationalLens(42)
        l.add_lens("heavy", 0, 0, 5.0)
        r = l.trace_ray(-5, -10, 0.1, 1.0)
        assert "deflection" in r; assert r["deflection"] > 0
    def test_demo(self):
        from lab.gravitational_lens import demo
        r = demo(); assert r["lenses"] == 5

class TestFractalComplexityAnalyzer:
    def test_demo(self):
        from lab.fractal_complexity_analyzer import demo
        r = demo(); assert r["files"] > 0; assert r["avg_fractal_dimension"] >= 0

class TestTemporalEchoEngine:
    def test_simulate(self):
        from lab.temporal_echo_engine import TemporalEchoEngine
        e = TemporalEchoEngine(echo_interval=3, seed=42)
        r = e.simulate(ticks=20)
        assert r["ticks"] == 20; assert r["total_echoes"] >= 0
    def test_demo(self):
        from lab.temporal_echo_engine import demo
        r = demo(); assert r["report"]["ticks"] == 30
