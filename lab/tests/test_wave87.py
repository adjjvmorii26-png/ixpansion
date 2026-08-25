from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

class TestMemeEvolutionEngine:
    def test_seed_and_evolve(self):
        from lab.meme_evolution_engine import MemePopulation
        e = MemePopulation(42); e.seed_memes(10)
        r = e.simulate(generations=5)
        assert r["generations"] == 5; assert r["final_population"] >= 1
    def test_demo(self):
        from lab.meme_evolution_engine import demo
        r = demo(); assert r["report"]["generation"] >= 0

class TestDreamArchaeology:
    def test_demo(self):
        from lab.dream_archaeology import demo
        r = demo(); assert r["total_artifacts"] == 50; assert r["recurring_symbols"] >= 0

class TestTemporalMusicTheory:
    def test_demo(self):
        from lab.temporal_music_theory import demo
        r = demo(); assert r["notes_composed"] > 0; assert "key_signature" in r

class TestNeuralPlasticitySimulator:
    def test_simulate(self):
        from lab.neural_plasticity_simulator import NeuralPlasticitySimulator
        s = NeuralPlasticitySimulator(42)
        for n in ["a","b","c"]: s.add_region(n)
        s.auto_connect(); r = s.simulate(ticks=10)
        assert r["ticks"] == 10
    def test_demo(self):
        from lab.neural_plasticity_simulator import demo
        r = demo(); assert r["report"]["regions"] == 6

class TestGravitationalTimeDilation:
    def test_demo(self):
        from lab.gravitational_time_dilation import demo
        r = demo(); assert r["body_count"] > 0; assert r["avg_dilation"] >= 0

class TestCosmicFabricWeaver:
    def test_demo(self):
        from lab.cosmic_fabric_weaver import demo
        r = demo(); assert r["point_count"] > 0; assert r["geodesics"] >= 0
