from __future__ import annotations
"""Tests for Wave 92 — Emergent Complexity experiments."""
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

def test_fractal_language():
    from lab.experiments.fractal_language import FractalLanguageEngine
    engine = FractalLanguageEngine(max_depth=3, seed=42)
    sym = engine.compose("A", ["B", "C"])
    assert len(sym.compose()) > 0
    sentence = engine.generate_sentence(length=3)
    assert len(sentence) > 0
    report = engine.grammar_report()
    assert report["vocabulary_size"] >= 1

def test_neural_dust():
    from lab.experiments.neural_dust import NeuralDustCloud
    cloud = NeuralDustCloud(width=50, height=50, num_particles=20, seed=42)
    zones = {"zone_a": (10, 10, 20, 20), "zone_b": (30, 30, 40, 40)}
    stats = cloud.run(steps=10, zones=zones)
    assert stats["particles_alive"] >= 0
    assert stats["total_collisions"] >= 0

def test_neural_dust_sensing():
    from lab.experiments.neural_dust import NeuralDustCloud
    cloud = NeuralDustCloud(width=50, height=50, num_particles=15, seed=42)
    cloud.sense_environment({"test_zone": (0, 0, 50, 50)})
    cloud.step()
    awareness = cloud.awareness_map()
    assert isinstance(awareness, dict)

def test_phase_transition():
    from lab.experiments.phase_transition import PhaseTransitionDetector, Phase
    detector = PhaseTransitionDetector()
    temps = [0.1] * 10 + [0.5] * 10 + [0.9] * 10
    transitions = 0
    for t in temps:
        result = detector.record(t)
        if result:
            transitions += 1
    assert transitions >= 1
    diagram = detector.phase_diagram()
    assert diagram["total_states"] == 30
    assert len(diagram["phase_distribution"]) >= 2

def test_phase_transition_stability():
    from lab.experiments.phase_transition import PhaseTransitionDetector
    detector = PhaseTransitionDetector()
    for _ in range(20):
        detector.record(0.5)
    stability = detector.stability_analysis()
    assert stability["stable"] is True

def test_strange_attractor():
    from lab.experiments.strange_attractor import StrangeAttractorMapper
    mapper = StrangeAttractorMapper()
    mapper.generate(x0=1.0, y0=1.0, z0=1.0, steps=500, system="lorenz")
    attractor = mapper.analyze("lorenz")
    assert attractor.basin_size == 500
    assert attractor.dimension > 0
    state = mapper.state()
    assert state["points"] == 500

def test_strange_attractor_rossler():
    from lab.experiments.strange_attractor import StrangeAttractorMapper
    mapper = StrangeAttractorMapper()
    mapper.generate(x0=1.0, y0=1.0, z0=1.0, steps=300, system="rossler")
    attractor = mapper.analyze("rossler")
    assert attractor.basin_size == 300

def test_quantum_error_correction():
    from lab.experiments.quantum_error_correction import QuantumErrorCorrectionEngine
    engine = QuantumErrorCorrectionEngine(seed=42)
    blocks = engine.encode([0, 1, 1, 0], method="bit_flip")
    assert len(blocks) == 4
    engine.inject_errors(error_rate=0.2)
    corrections = engine.correct()
    assert corrections >= 0
    state = engine.state()
    assert state["overhead"]["overhead_ratio"] == 3.0

def test_quantum_error_correction_shor():
    from lab.experiments.quantum_error_correction import QuantumErrorCorrectionEngine
    engine = QuantumErrorCorrectionEngine(seed=42)
    blocks = engine.encode([1, 0, 1], method="shor")
    assert len(blocks) == 3
    assert all(len(b.data_qubits) == 9 for b in blocks)

def test_topological_insulator():
    from lab.experiments.topological_insulator import TopologicalInsulator
    ti = TopologicalInsulator()
    ti.add_node("bulk_1", is_edge=False)
    ti.add_node("edge_1", is_edge=True)
    ti.add_node("edge_2", is_edge=True)
    ti.connect("edge_1", "edge_2", protected=True)
    ti.connect("bulk_1", "edge_1", protected=False)
    ti.send("edge_1", "edge_2", "protected_msg")
    ti.send("bulk_1", "edge_1", "blocked_msg")
    stats = ti.transmission_stats()
    assert stats["passed"] >= 1
    assert stats["blocked"] >= 1
    topo = ti.topology_map()
    assert topo["edge_nodes"] == ["edge_1", "edge_2"]

def test_emergent_grammar():
    from lab.experiments.emergent_grammar import EmergentGrammarEngine
    engine = EmergentGrammarEngine(num_agents=5, seed=42)
    result = engine.run(rounds=200)
    assert result["rounds"] == 200
    assert result["vocabulary_size"] >= 1
    assert 0 <= result["success_rate"] <= 1.0
    convergence = engine.convergence_report()
    assert "converged" in convergence

def test_dark_energy():
    from lab.experiments.dark_energy import DarkEnergyEngine
    engine = DarkEnergyEngine(dark_energy_density=0.7)
    engine.add_body("a", mass=10.0, position=0.0)
    engine.add_body("b", mass=5.0, position=5.0)
    for _ in range(50):
        engine.step()
    state = engine.state()
    assert state["scale_factor"] > 1.0
    assert state["tick"] == 50

def test_cosmic_web_structure():
    from lab.experiments.cosmic_web_structure import CosmicWebMapper
    mapper = CosmicWebMapper()
    for name in ["a", "b", "c", "d"]:
        mapper.add_module(name, mass=1.0)
    mapper.add_dependency("a", "b")
    mapper.add_dependency("c", "d")
    mapper.map_web()
    summary = mapper.summary()
    assert summary["modules"] == 4
    assert summary["galaxies"] >= 1

def test_information_entropy_decay():
    from lab.experiments.information_entropy_decay import InformationEntropyDecay
    engine = InformationEntropyDecay(seed=42)
    engine.store("test_data", "hello world", decay_constant=0.02)
    history = engine.run(ticks=50)
    assert len(history) == 50
    report = engine.survival_report()
    assert report["total_packets"] == 1
    curve = engine.build_decay_curve("test_data")
    assert curve is not None
    assert curve.estimated_half_life > 0

def test_information_decay_multiple():
    from lab.experiments.information_entropy_decay import InformationEntropyDecay
    engine = InformationEntropyDecay(seed=42)
    engine.store("fast", "data1", decay_constant=0.1)
    engine.store("slow", "data2", decay_constant=0.001)
    engine.run(ticks=50)
    report = engine.survival_report()
    assert report["total_packets"] == 2

def test_wave92_all_demos():
    from lab.experiments.fractal_language import demo as fl_demo
    from lab.experiments.neural_dust import demo as nd_demo
    from lab.experiments.phase_transition import demo as pt_demo
    from lab.experiments.strange_attractor import demo as sa_demo
    from lab.experiments.quantum_error_correction import demo as qec_demo
    from lab.experiments.topological_insulator import demo as ti_demo
    from lab.experiments.emergent_grammar import demo as eg_demo
    from lab.experiments.dark_energy import demo as de_demo
    from lab.experiments.cosmic_web_structure import demo as cws_demo
    from lab.experiments.information_entropy_decay import demo as ied_demo
    for demo_fn in [fl_demo, nd_demo, pt_demo, sa_demo, qec_demo,
                    ti_demo, eg_demo, de_demo, cws_demo, ied_demo]:
        result = demo_fn()
        assert result is not None
