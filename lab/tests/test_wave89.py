from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

class TestRealityFabricSimulator:
    def test_simulate(self):
        from lab.reality_fabric_simulator import RealityFabricSimulator
        s = RealityFabricSimulator(42, 5, 5)
        r = s.simulate(ticks=10)
        assert r["ticks"] == 10; assert r["nodes"] == 25
    def test_demo(self):
        from lab.reality_fabric_simulator import demo
        r = demo(); assert r["report"]["nodes"] > 0

class TestQuantumSuperpositionEngine:
    def test_measure(self):
        from lab.quantum_superposition_engine import QuantumSuperpositionEngine
        e = QuantumSuperpositionEngine(42)
        e.add_module("test")
        m = e.measure_all()
        assert len(m) == 1
    def test_demo(self):
        from lab.quantum_superposition_engine import demo
        r = demo(); assert r["modules"] > 0

class TestNeuralNetworkMapper:
    def test_demo(self):
        from lab.neural_network_mapper import demo
        r = demo(); assert r["layers"] == 4; assert r["classified"] > 0

class TestCosmicRayDetector:
    def test_simulate(self):
        from lab.cosmic_ray_detector import CosmicRayDetector
        d = CosmicRayDetector(42)
        r = d.simulate(ray_count=10)
        assert r["rays"] == 10; assert r["impacts"] == 10
    def test_demo(self):
        from lab.cosmic_ray_detector import demo
        r = demo(); assert r["simulation"]["rays"] == 30

class TestSpacetimeManifold:
    def test_simulate(self):
        from lab.spacetime_manifold import SpacetimeManifold
        m = SpacetimeManifold(42)
        for i in range(5): m.add_event(f"e{i}", i, i, i, 0)
        r = m.simulate(ticks=10)
        assert r["events"] == 5; assert r["light_cones"] > 0
    def test_demo(self):
        from lab.spacetime_manifold import demo
        r = demo(); assert r["report"]["events"] == 8

class TestDimensionalFoldAnalyzer:
    def test_demo(self):
        from lab.dimensional_fold_analyzer import demo
        r = demo(); assert r["dimensions"] == 4; assert r["points"] == 10
