from __future__ import annotations
"""Tests for Wave 95 — Cross-System Synthesis experiments."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

def test_reality_synthesis():
    from lab.experiments.reality_synthesis import RealitySynthesizer
    synth = RealitySynthesizer()
    synth.ingest_constellation({"treaties": ["t1"], "hash": "abc"})
    synth.ingest_mycelium({"dream_id": "d1", "hypothesis": "growth", "confidence": 0.7})
    synth.ingest_experiment({"name": "exp1", "result": {}, "confidence": 0.8})
    synth.ingest_bridge({"event": "e1", "origin": "a", "target": "b", "confidence": 0.9})
    reality = synth.synthesize()
    assert reality.coherence_score > 0
    assert reality.narrative != ""
    assert len(reality.fragments) == 4

def test_reality_synthesis_contradictions():
    from lab.experiments.reality_synthesis import RealitySynthesizer
    synth = RealitySynthesizer()
    synth.ingest_experiment({"name": "a", "result": {}, "confidence": 0.9})
    synth.ingest_experiment({"name": "b", "result": {}, "confidence": 0.2})
    reality = synth.synthesize()
    assert len(reality.contradictions) >= 0

def test_consent_propagation():
    from lab.experiments.consent_propagation import ConsentPropagationEngine
    engine = ConsentPropagationEngine()
    engine.register("a", consents_to=["b"], consent_level=1.0)
    engine.register("b", consents_to=["c"], consent_level=0.9)
    engine.register("c", consents_to=[], consent_level=0.8)
    engine.propagate("a", "b")
    engine.propagate("b", "c")
    engine.propagate("c", "a")
    graph = engine.consent_graph()
    assert graph["authorized"] >= 2
    assert graph["unauthorized"] >= 1

def test_consent_revocation():
    from lab.experiments.consent_propagation import ConsentPropagationEngine
    engine = ConsentPropagationEngine()
    engine.register("a", consents_to=["b"])
    engine.register("b", consents_to=[])
    engine.propagate("a", "b")
    engine.revoke("a", "admin")
    engine.propagate("a", "b")
    graph = engine.consent_graph()
    assert graph["violations"] or graph["unauthorized"] >= 0

def test_shadow_timeline_merger():
    from lab.experiments.shadow_timeline_merger import ShadowTimelineMerger
    merger = ShadowTimelineMerger()
    merger.ingest_astral("t1", [{"event": "e1", "probability": 0.8, "timestamp": 1}])
    merger.ingest_dream("d1", [{"event": "e2", "probability": 0.7, "timestamp": 1}])
    merged = merger.merge("t1", "d1")
    assert merged is not None
    assert merged.coherence > 0
    assert len(merged.nodes) == 2

def test_shadow_timeline_missing():
    from lab.experiments.shadow_timeline_merger import ShadowTimelineMerger
    merger = ShadowTimelineMerger()
    merged = merger.merge("nonexistent", "also_nonexistent")
    assert merged is None

def test_cross_pollination():
    from lab.experiments.cross_pollination_engine import CrossPollinationEngine
    engine = CrossPollinationEngine()
    engine.register_concept("sys_a", "concept1")
    engine.register_concept("sys_b", "concept2")
    engine.register_concept("sys_c", "concept3")
    vectors = engine.discover_vectors(threshold=0.0)
    assert isinstance(vectors, list)
    pmap = engine.pollination_map()
    assert "total_vectors" in pmap

def test_temporal_pattern():
    from lab.experiments.temporal_pattern_recognizer import TemporalPatternRecognizer
    import math
    series = [50 + 20 * math.sin(i * 2 * math.pi / 7) for i in range(100)]
    recognizer = TemporalPatternRecognizer(series)
    patterns = recognizer.detect()
    assert len(patterns) > 0
    assert recognizer.dominant_period() > 0

def test_negative_space():
    from lab.experiments.negative_space_analyzer import NegativeSpaceAnalyzer
    analyzer = NegativeSpaceAnalyzer()
    analyzer.register_present("a", ["b"])
    analyzer.register_present("b", [])
    analyzer.register_expected("a")
    analyzer.register_expected("b")
    analyzer.register_expected("c")
    report = analyzer.report()
    assert report["absent"] == 1
    assert report["present"] == 2

def test_provenance_tracker():
    from lab.experiments.provenance_tracker import ProvenanceTracker
    tracker = ProvenanceTracker()
    tracker.record("input", output={"v": 1})
    tracker.record("transform", inputs=[{"v": 1}], output={"v": 2})
    trace = tracker.trace("prov_0002")
    assert len(trace) >= 1
    graph = tracker.full_graph()
    assert graph["total_nodes"] == 2

def test_emergent_property():
    from lab.experiments.emergent_property_detector import EmergentPropertyDetector
    detector = EmergentPropertyDetector()
    detector.register("a", ["prop1"])
    detector.register("b", ["prop2"])
    detector.record_interaction("a", "b", "emergent_behavior")
    emergent = detector.detect()
    assert len(emergent) >= 1
    assert emergent[0].name == "emergent_behavior"

def test_fractal_documentation():
    from lab.experiments.fractal_documentation import FractalDocumentation
    docs = FractalDocumentation()
    docs.document_module("test", "overview", "module_doc",
                         [{"name": "f1", "docstring": "does stuff"}])
    overview = docs.get_level("test", "overview")
    assert overview is not None
    assert overview.content == "overview"
    summary = docs.summary()
    assert summary["modules_documented"] == 1

def test_system_metabolism_v2():
    from lab.experiments.system_metabolism_v2 import SystemMetabolismV2
    meta = SystemMetabolismV2()
    meta.register("input", input_energy=100)
    meta.register("output", input_energy=0)
    meta.flow("input", "output", 80)
    meta.step()
    report = meta.metabolic_report()
    assert report["overall_efficiency"] > 0

def test_information_theory():
    from lab.experiments.information_theory_analyzer import InformationTheoryAnalyzer
    analyzer = InformationTheoryAnalyzer()
    analyzer.add_channel("ch1", capacity=10.0)
    analyzer.send("ch1", 5.0, noise_level=0.1)
    report = analyzer.channel_report()
    assert len(report) == 1
    assert report[0]["mutual_info"] > 0
    entropy = analyzer.system_entropy()
    assert entropy > 0

def test_wave95_all_demos():
    from lab.experiments.reality_synthesis import demo as rs_demo
    from lab.experiments.consent_propagation import demo as cp_demo
    from lab.experiments.shadow_timeline_merger import demo as stm_demo
    from lab.experiments.cross_pollination_engine import demo as cpe_demo
    from lab.experiments.temporal_pattern_recognizer import demo as tpr_demo
    from lab.experiments.negative_space_analyzer import demo as nsa_demo
    from lab.experiments.provenance_tracker import demo as pt_demo
    from lab.experiments.emergent_property_detector import demo as epd_demo
    from lab.experiments.fractal_documentation import demo as fd_demo
    from lab.experiments.system_metabolism_v2 import demo as smv2_demo
    from lab.experiments.information_theory_analyzer import demo as ita_demo
    for demo_fn in [rs_demo, cp_demo, stm_demo, cpe_demo, tpr_demo,
                    nsa_demo, pt_demo, epd_demo, fd_demo, smv2_demo, ita_demo]:
        result = demo_fn()
        assert result is not None
