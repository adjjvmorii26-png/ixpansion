from __future__ import annotations
"""Tests for Wave 91 — Quantum Archaeology experiments."""
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

def test_fossilized_code_analyzer():
    from lab.experiments.fossilized_code_analyzer import FossilizedCodeAnalyzer, CodeFossilType
    analyzer = FossilizedCodeAnalyzer()
    analyzer.record_era("primordial", 100, ["a", "b"], 2)
    analyzer.record_era("expansion", 200, ["c", "d"], 5)
    analyzer.register_fossil("old_func", CodeFossilType.ORPHAN_FUNCTION, 0.7, ["json"], 500)
    analyzer.register_fossil("dead_mod", CodeFossilType.DEPRECATED_MODULE, 0.9, ["db"], 800)
    report = analyzer.generate_report()
    assert report["fossils"] == 2
    assert report["eras"] == 2
    assert len(report["complexity_trend"]) == 2

def test_fossilized_lineage():
    from lab.experiments.fossilized_code_analyzer import FossilizedCodeAnalyzer, CodeFossilType
    analyzer = FossilizedCodeAnalyzer()
    analyzer.register_fossil("parser_v1", CodeFossilType.ORPHAN_FUNCTION, 0.6, ["parser"], 100)
    analyzer.register_fossil("parser_v2", CodeFossilType.GHOST_CLASS, 0.8, ["parser"], 200)
    lineage = analyzer.analyze_lineage("parser")
    assert lineage["related_fossils"] >= 1

def test_dream_weaver():
    from lab.experiments.dream_weaver import DreamWeaver
    weaver = DreamWeaver(seed=42)
    dream = weaver.weave({"entropy": 0.8, "failures": 5})
    assert dream.symbols is not None
    assert len(dream.symbols) > 0
    assert dream.narrative != ""
    assert dream.emotional_tone in ["lucid", "fragmented", "coherent", "nightmarish",
                                     "ethereal", "prophetic", "nostalgic", "alien"]

def test_dream_weaver_archive():
    from lab.experiments.dream_weaver import DreamWeaver
    weaver = DreamWeaver(seed=42)
    for i in range(5):
        weaver.weave({"entropy": i * 0.2, "connections": i * 3})
    journal = weaver.dream_journal()
    assert len(journal) == 5
    assert all("narrative" in d for d in journal)

def test_dream_weaver_compare():
    from lab.experiments.dream_weaver import DreamWeaver
    weaver = DreamWeaver(seed=42)
    weaver.weave({"failures": 8, "connections": 3, "temp_a": 50, "temp_b": 20})
    weaver.weave({"failures": 0, "connections": 15, "temp_a": 22, "temp_b": 30})
    comparison = weaver.compare_dreams(0, 1)
    assert "shared_symbols" in comparison
    assert "entropy_diff" in comparison

def test_time_dilation_field():
    from lab.experiments.time_dilation_field import TimeDilationField, C
    td = TimeDilationField()
    td.add_body("fast", mass=1.0, velocity=C * 0.9)
    td.add_body("slow", mass=100.0, velocity=0)
    result = td.run(steps=20)
    assert result["steps"] == 20
    assert result["fastest_ticks"] > result["slowest_ticks"]

def test_time_dilation_lorentz():
    from lab.experiments.time_dilation_field import TemporalBody, C
    body = TemporalBody(name="test", mass=1.0, velocity=C * 0.8)
    assert body.lorentz_factor > 1.0
    assert body.total_dilation > 0

def test_quantum_tunneling():
    from lab.experiments.quantum_tunneling import QuantumTunnelingEngine
    engine = QuantumTunnelingEngine(seed=42)
    engine.add_state("electron", energy=3.0)
    engine.add_barrier("wall", width=1.0, height=5.0)
    result = engine.run_scenario("electron", 0, attempts=100)
    assert result["attempts"] == 100
    assert 0 <= result["empirical_rate"] <= 1.0
    assert result["theoretical_rate"] > 0

def test_quantum_tunneling_high_energy():
    from lab.experiments.quantum_tunneling import QuantumTunnelingEngine
    engine = QuantumTunnelingEngine(seed=42)
    engine.add_state("proton", energy=10.0)
    engine.add_barrier("weak_wall", width=0.5, height=2.0)
    result = engine.run_scenario("proton", 0, attempts=50)
    assert result["empirical_rate"] > 0.8

def test_morphic_resonance():
    from lab.experiments.morphic_resonance import MorphicResonanceDetector
    detector = MorphicResonanceDetector(seed=42)
    detector.add_module("alpha", frequency=1.0, amplitude=1.0, phase=0.0)
    detector.add_module("beta", frequency=1.0, amplitude=0.8, phase=0.1)
    detector.add_module("gamma", frequency=3.0, amplitude=1.0, phase=2.0)
    pairs = detector.detect(correlation_threshold=0.5)
    assert isinstance(pairs, list)
    report = detector.resonance_report()
    assert report["modules"] == 3

def test_morphic_resonance_perturb():
    from lab.experiments.morphic_resonance import MorphicResonanceDetector
    detector = MorphicResonanceDetector(seed=42)
    detector.add_module("a", frequency=1.0, phase=0.0)
    detector.add_module("b", frequency=1.0, phase=0.05)
    pairs_before = detector.detect(correlation_threshold=0.9)
    detector.perturb("b", delta_freq=0.5, delta_phase=1.0)
    pairs_after = detector.detect(correlation_threshold=0.9)
    assert len(pairs_after) <= len(pairs_before) + 5

def test_dimensional_fold():
    from lab.experiments.dimensional_fold import DimensionalFolder
    folder = DimensionalFolder(target_dim=3)
    for i in range(8):
        folder.add_node(f"node_{i}")
    for i in range(7):
        folder.add_edge(f"node_{i}", f"node_{i+1}")
    folder.add_edge("node_0", "node_3")
    folder.add_edge("node_2", "node_5")
    result = folder.fold()
    assert result.original_edges > 0
    assert result.cluster_count >= 1
    state = folder.state()
    assert state["dimension"] == 3

def test_chronicle_loom():
    from lab.experiments.chronicle_loom import ChronicleLoom
    loom = ChronicleLoom()
    for i in range(10):
        loom.record_event("nucleus", "heartbeat", f"tick_{i}")
        loom.record_event("agents", "action", f"action_{i}")
    tapestry = loom.weave()
    assert len(tapestry.events) == 20
    assert tapestry.thread_count == 2
    analysis = loom.pattern_analysis()
    assert analysis["total_crossings"] >= 0

def test_paradox_bloom():
    from lab.experiments.paradox_bloom import ParadoxBloomEngine, ParadoxType
    engine = ParadoxBloomEngine(seed=42)
    engine.create_paradox("liar", ParadoxType.SELF_REFERENCE, "true", "false")
    engine.create_paradox("loop", ParadoxType.TEMPORAL, "A_causes_B", "B_causes_A")
    results = engine.bloom_all()
    assert len(results) == 2
    for r in results:
        assert r.narrative != ""
        assert r.residual_energy >= 0

def test_paradox_bloom_resolution():
    from lab.experiments.paradox_bloom import ParadoxBloomEngine, ParadoxType
    engine = ParadoxBloomEngine(seed=42)
    engine.create_paradox("test", ParadoxType.CONTRADICTION, "up", "down")
    result = engine.resolve("test")
    assert result is not None
    assert result.strategy is not None
    stats = engine.resolution_stats()
    assert stats["resolved"] == 1

def test_genetic_memory():
    from lab.experiments.genetic_memory import GeneticMemoryEngine
    engine = GeneticMemoryEngine(seed=42)
    engine.create_organism("alpha", "Hello genetic world")
    engine.create_organism("beta", "Memory evolves")
    assert len(engine.organisms) == 2
    history = engine.run_evolution(generations=10)
    assert len(history) == 10
    report = engine.population_report()
    assert report["population"] >= 2

def test_genetic_memory_crossover():
    from lab.experiments.genetic_memory import GeneticMemoryEngine
    engine = GeneticMemoryEngine(seed=42)
    engine.create_organism("parent_a", "First parent")
    engine.create_organism("parent_b", "Second parent")
    child = engine.crossover("parent_a", "parent_b")
    assert child is not None
    assert child.genome.generation == engine.generation

def test_entropy_weather_forecast():
    from lab.experiments.entropy_weather_forecast import EntropyWeatherForecast, EntropyWeather
    forecaster = EntropyWeatherForecast(seed=42)
    values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    for v in values:
        forecaster.record(v)
    assert len(forecaster.readings) == 8
    forecast = forecaster.forecast(horizon=3)
    assert forecast.predicted_weather is not None
    assert 0 <= forecast.confidence <= 1.0

def test_entropy_weather_summary():
    from lab.experiments.entropy_weather_forecast import EntropyWeatherForecast
    forecaster = EntropyWeatherForecast(seed=42)
    for i in range(20):
        forecaster.record(0.1 + (i % 5) * 0.15)
    summary = forecaster.summary()
    assert summary["total_readings"] == 20
    assert summary["current_weather"] in ["calm", "breezy", "storm", "hurricane", "drought", "monsoon"]

def test_wave91_all_demos():
    from lab.experiments.fossilized_code_analyzer import demo as fca_demo
    from lab.experiments.dream_weaver import demo as dw_demo
    from lab.experiments.time_dilation_field import demo as tdf_demo
    from lab.experiments.quantum_tunneling import demo as qt_demo
    from lab.experiments.morphic_resonance import demo as mr_demo
    from lab.experiments.dimensional_fold import demo as df_demo
    from lab.experiments.chronicle_loom import demo as cl_demo
    from lab.experiments.paradox_bloom import demo as pb_demo
    from lab.experiments.genetic_memory import demo as gm_demo
    from lab.experiments.entropy_weather_forecast import demo as ewf_demo
    for demo_fn in [fca_demo, dw_demo, tdf_demo, qt_demo, mr_demo,
                    df_demo, cl_demo, pb_demo, gm_demo, ewf_demo]:
        result = demo_fn()
        assert result is not None
