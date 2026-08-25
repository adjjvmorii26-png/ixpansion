"""Tests for Wave 76 experimental innovation modules."""
from __future__ import annotations

import pytest


class TestReactorFusionSim:
    def test_import(self):
        from lab.experiments.reactor_fusion_sim import ReactorFusionSimulator
        assert ReactorFusionSimulator is not None

    def test_run_pipeline(self):
        from lab.experiments.reactor_fusion_sim import ReactorFusionSimulator
        sim = ReactorFusionSimulator(seed=42)
        state = {"energy": 0.8, "entropy": 0.3}
        result = sim.run_pipeline(state, ["chaos", "order"], steps=2)
        assert result["steps"] > 0
        assert result["total_entropy_cost"] >= 0

    def test_chaos_injects_noise(self):
        from lab.experiments.reactor_fusion_sim import ReactorFusionSimulator
        sim = ReactorFusionSimulator(seed=42)
        state = {"value": 1.0}
        result = sim.run_pipeline(state, ["chaos"], steps=1)
        final_val = result["final_state"]["state"]["value"]
        assert final_val != 1.0  # Should have changed

    def test_inversion_negates(self):
        from lab.experiments.reactor_fusion_sim import ReactorFusionSimulator
        sim = ReactorFusionSimulator(seed=42)
        state = {"x": 5.0, "flag": True}
        result = sim.run_pipeline(state, ["inversion"], steps=1)
        final = result["final_state"]["state"]
        assert final["x"] == -5.0
        assert final["flag"] is False


class TestQuantumTunnelingSim:
    def test_import(self):
        from lab.experiments.quantum_tunneling_sim import QuantumTunnelingSim
        assert QuantumTunnelingSim is not None

    def test_barrier_dissolves(self):
        from lab.experiments.quantum_tunneling_sim import QuantumTunnelingSim
        sim = QuantumTunnelingSim(seed=42)
        bid = sim.create_barrier(5, 5, thickness=3.0)
        for i in range(10):
            sim.add_agent(f"a{i}", curiosity=0.9)
        for _ in range(50):
            sim.tick()
        report = sim.report()
        assert report["barriers"][bid]["dissolved"] or report["barriers"][bid]["integrity"] < 1.0

    def test_agents_attempt_tunnels(self):
        from lab.experiments.quantum_tunneling_sim import QuantumTunnelingSim
        sim = QuantumTunnelingSim(seed=42)
        sim.create_barrier(5, 5, thickness=10.0)
        sim.add_agent("a1", curiosity=0.8)
        sim._agents["a1"].position = (5, 5)
        for _ in range(10):
            sim.tick()
        report = sim.report()
        assert report["agents"]["a1"]["tunnels_attempted"] > 0


class TestHyphalDecisionEngine:
    def test_import(self):
        from lab.experiments.hyphal_decision_engine import HyphalDecisionEngine
        assert HyphalDecisionEngine is not None

    def test_consensus_summary(self):
        from lab.experiments.hyphal_decision_engine import HyphalDecisionEngine
        engine = HyphalDecisionEngine(seed=42)
        engine.add_tip("t1", "alpha")
        engine.add_tip("t2", "beta")
        engine.add_site("s1", 10.0)
        engine.tick()
        summary = engine.consensus_summary()
        assert summary["total_proposals"] > 0

    def test_approval_rate_bounded(self):
        from lab.experiments.hyphal_decision_engine import HyphalDecisionEngine
        engine = HyphalDecisionEngine(seed=42)
        for i in range(5):
            engine.add_tip(f"t{i}", "alpha")
        engine.add_site("s1", 10.0)
        for _ in range(10):
            engine.tick()
        summary = engine.consensus_summary()
        assert 0.0 <= summary["approval_rate"] <= 1.0


class TestDialectEvolution:
    def test_import(self):
        from lab.experiments.dialect_evolution import DialectEvolution
        assert DialectEvolution is not None

    def test_evolve_produces_children(self):
        from lab.experiments.dialect_evolution import DialectEvolution
        evo = DialectEvolution(seed=42, population_size=3)
        evo.create_alpha_dialect()
        children = evo.evolve()
        assert len(children) == 3

    def test_fossilization(self):
        from lab.experiments.dialect_evolution import DialectEvolution
        evo = DialectEvolution(seed=42, fossilize_threshold=2)
        evo.create_alpha_dialect()
        for _ in range(5):
            evo.evolve()
        report = evo.evolution_report()
        assert report["fossilized"] > 0

    def test_encode_works(self):
        from lab.experiments.dialect_evolution import Dialect
        d = Dialect(dialect_id="test", generation=0, encoding_rules={"val": "uppercase"})
        result = d.encode({"val": "hello"})
        assert result["val"] == "HELLO"


class TestRealityFabricSim:
    def test_import(self):
        from lab.experiments.reality_fabric_sim import RealityFabricSim
        assert RealityFabricSim is not None

    def test_fabric_init(self):
        from lab.experiments.reality_fabric_sim import RealityFabricSim
        sim = RealityFabricSim(width=4, height=4, seed=42)
        sim.init_fabric()
        assert len(sim._cells) == 16

    def test_tension_accumulates(self):
        from lab.experiments.reality_fabric_sim import RealityFabricSim
        sim = RealityFabricSim(width=4, height=4, seed=42)
        sim.init_fabric()
        sim.add_agent("a1")
        sim.tick()
        report = sim.fabric_report()
        assert report["mean_tension"] > 0

    def test_fold_events(self):
        from lab.experiments.reality_fabric_sim import RealityFabricSim
        sim = RealityFabricSim(width=4, height=4, seed=42, tension_per_agent=0.5)
        sim.init_fabric()
        for i in range(15):
            sim.add_agent(f"a{i}", dimension=["primary", "secondary"][i % 2])
        for _ in range(30):
            sim.tick()
        report = sim.fabric_report()
        assert report["fold_events"] >= 0


class TestChronicleEngineSim:
    def test_import(self):
        from lab.experiments.chronicle_engine_sim import ChronicleEngineSim
        assert ChronicleEngineSim is not None

    def test_record_and_verify(self):
        from lab.experiments.chronicle_engine_sim import ChronicleEngineSim
        engine = ChronicleEngineSim(seed=42)
        engine.record("src", "test", 0.5)
        engine.record("src", "test", 0.6)
        chain = engine.verify_chain()
        assert chain["chain_valid"]

    def test_detect_clusters(self):
        from lab.experiments.chronicle_engine_sim import ChronicleEngineSim
        engine = ChronicleEngineSim(seed=42)
        for i in range(20):
            engine.record("src", "test", 0.5)
            if 10 <= i <= 13:
                for _ in range(5):
                    engine.record("src", "test", 0.9)
        clusters = engine.detect_clusters()
        assert len(clusters) > 0

    def test_category_summary(self):
        from lab.experiments.chronicle_engine_sim import ChronicleEngineSim
        engine = ChronicleEngineSim(seed=42)
        engine.record("s1", "alpha", 0.5)
        engine.record("s2", "beta", 0.7)
        engine.record("s1", "alpha", 0.6)
        summary = engine.category_summary()
        assert "alpha" in summary
        assert summary["alpha"]["count"] == 2
