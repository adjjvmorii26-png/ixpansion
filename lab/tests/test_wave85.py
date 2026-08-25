from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

class TestConsciousnessSimulator:
    def test_neuron_fire(self):
        from lab.consciousness_simulator import Neuron
        n = Neuron(0, 42)
        n.receive(1.0)
        out = n.fire()
        assert out >= 0
    def test_simulate(self):
        from lab.consciousness_simulator import ConsciousnessSubstrate
        s = ConsciousnessSubstrate(size=20, seed=42)
        r = s.simulate(ticks=30)
        assert r["ticks"] == 30; assert r["final_awareness"] >= 0
    def test_demo(self):
        from lab.consciousness_simulator import demo
        r = demo(); assert "simulation" in r; assert "report" in r

class TestTemporalArchaeologist:
    def test_demo(self):
        from lab.temporal_archaeologist import demo
        r = demo(); assert r["commits_analyzed"] > 0; assert r["waves_found"] > 0

class TestQuantumClassifier:
    def test_measure(self):
        from lab.quantum_classifier import QuantumClassifier
        qc = QuantumClassifier(42)
        import pathlib; qc.register_module("test", pathlib.Path("lab/cli.py"))
        m = qc.measure_all(); assert len(m) == 1
    def test_demo(self):
        from lab.quantum_classifier import demo
        r = demo(); assert r["module_count"] > 0; assert r["measurements"] > 0

class TestGravitationalAnalyzer:
    def test_tick(self):
        from lab.gravitational_analyzer import GravitationalSystem
        s = GravitationalSystem(42)
        s.add_body("a", 1.0, 0, 0); s.add_body("b", 2.0, 3, 0)
        s.tick(); assert s.tick_count == 1
    def test_simulate(self):
        from lab.gravitational_analyzer import GravitationalSystem
        s = GravitationalSystem(42)
        s.add_body("a", 1.0, 0, 0); s.add_body("b", 2.0, 3, 0)
        r = s.simulate(ticks=10); assert r["ticks"] == 10
    def test_demo(self):
        from lab.gravitational_analyzer import demo
        r = demo(); assert r["report"]["bodies"] > 0

class TestNeuralPathwayMapper:
    def test_demo(self):
        from lab.neural_pathway_mapper import demo
        r = demo(); assert r["mapper"] == "neural_pathway_mapper"; assert r["scan_count"] == 3

class TestCosmicWebMapper:
    def test_demo(self):
        from lab.cosmic_web_mapper import demo
        r = demo(); assert r["galaxies"] > 0; assert r["total_stars"] > 0
