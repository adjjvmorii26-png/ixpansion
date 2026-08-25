from __future__ import annotations
"""Tests for Wave 93 — Computational Folklore experiments."""
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

def test_urban_legend():
    from lab.experiments.urban_legend_engine import UrbanLegendEngine
    engine = UrbanLegendEngine(seed=42)
    engine.create_legend("test", "def foo(): pass")
    for _ in range(10):
        engine.tell("test", "module_a", mutation_rate=0.05)
    report = engine.folklore_report()
    assert report["total_legends"] == 1
    assert report["total_tells"] == 10

def test_urban_legend_mutation():
    from lab.experiments.urban_legend_engine import UrbanLegendEngine
    engine = UrbanLegendEngine(seed=42)
    legend = engine.create_legend("mut", "original_code")
    original = legend.current
    engine.tell("mut", "teller", mutation_rate=0.3)
    assert legend.generation == 1
    assert legend.spread_count == 1

def test_alchemy_transmutation():
    from lab.experiments.alchemy_transmutation import AlchemyEngine
    alchemy = AlchemyEngine()
    r1 = alchemy._transmute("hello", "int")
    assert r1.success
    assert isinstance(r1.target_value, int)
    r2 = alchemy._transmute(42, "str")
    assert r2.success
    assert r2.target_value == "42"
    r3 = alchemy._transmute([1, 2], "tuple")
    assert r3.success
    assert isinstance(r3.target_value, tuple)
    report = alchemy.purity_report()
    assert report["successful"] >= 3

def test_alchemy_chain():
    from lab.experiments.alchemy_transmutation import AlchemyEngine
    alchemy = AlchemyEngine()
    chain = alchemy.transmute_chain("hello", ["list", "tuple", "str"])
    assert len(chain) == 3
    assert all(r.success for r in chain)

def test_myth_generator():
    from lab.experiments.myth_generator import MythGenerator
    gen = MythGenerator(seed=42)
    myth = gen.generate("nucleus")
    assert myth.narrative != ""
    assert myth.archetype in ["hero", "trickster", "sage", "creator", "destroyer", "guardian"]
    pantheon = gen.pantheon()
    assert "nucleus" in pantheon

def test_myth_multiple():
    from lab.experiments.myth_generator import MythGenerator
    gen = MythGenerator(seed=42)
    for name in ["a", "b", "c", "d"]:
        gen.generate(name)
    report = gen.myth_report()
    assert report["total_myths"] == 4

def test_cargo_cult_detector():
    from lab.experiments.cargo_cult_detector import CargoCultDetector
    detector = CargoCultDetector()
    findings = detector.scan_module("test", [
        {"name": "stub", "body": "pass", "calls": [],
         "complexity": 1, "dead_imports": [], "unused_vars": [], "placebo_calls": []},
        {"name": "real", "body": "return x", "calls": ["return"],
         "complexity": 2, "dead_imports": [], "unused_vars": [], "placebo_calls": []},
    ])
    assert len(findings) >= 1
    summary = detector.summary()
    assert summary["total_findings"] >= 1

def test_cargo_cult_placebo():
    from lab.experiments.cargo_cult_detector import CargoCultDetector
    detector = CargoCultDetector()
    findings = detector.scan_module("mod", [
        {"name": "fake", "body": "x = 1", "calls": [],
         "complexity": 1, "dead_imports": ["os"], "unused_vars": ["temp"],
         "placebo_calls": ["validate"]},
    ])
    types = [f.finding_type for f in findings]
    assert "dead_import" in types or "unused_vars" in types or "placebo" in types

def test_soup_of_life():
    from lab.experiments.soup_of_life import SoupOfLife
    soup = SoupOfLife(width=15, height=15, seed=42)
    soup.seed(density=0.3)
    initial = len([c for c in soup.grid.values() if c.alive])
    assert initial > 0
    history = soup.run(ticks=10)
    assert len(history) == 10
    report = soup.dish_report()
    assert "cells_alive" in report

def test_language_drift():
    from lab.experiments.language_drift import LanguageDriftTracker
    tracker = LanguageDriftTracker()
    tracker.track("fetch_data", "api")
    for _ in range(5):
        tracker.evolve("fetch_data", "api")
    analysis = tracker.drift_analysis()
    assert analysis["tracked_names"] == 1
    assert analysis["total_drift_events"] == 5

def test_ritual_automation():
    from lab.experiments.ritual_automation import RitualAutomation
    auto = RitualAutomation()
    auto.register_handler("echo", lambda x: f"echo:{x}")
    auto.create_ritual("test_ritual", [
        {"name": "step1", "command": "echo", "offering": "data"},
        {"name": "step2", "command": "echo", "offering": "result"},
    ], repetitions=2)
    result = auto.perform("test_ritual")
    assert len(result["results"]) == 4
    summary = auto.summary()
    assert summary["performed"] == 1

def test_folk_taxonomist():
    from lab.experiments.folk_taxonomist import FolkTaxonomist
    tax = FolkTaxonomist()
    fc = tax.classify("nucleus", {"has_state": 0.9, "complexity": 0.8})
    assert fc.primary_role in ["keeper", "messenger", "weaver", "watcher",
                                "builder", "breaker", "dreamer", "walker",
                                "singer", "healer"]
    assert fc.folk_name != ""
    report = tax.taxonomy_report()
    assert report["total_classified"] == 1

def test_oral_tradition():
    from lab.experiments.oral_tradition import OralTraditionEngine
    engine = OralTraditionEngine(seed=42)
    engine.create_story("story1", "elder", "original message")
    for _ in range(10):
        engine.tell("story1", "agent_a", "agent_b", corruption_rate=0.02)
    health = engine.tradition_health()
    assert health["total_stories"] == 1
    assert health["total_tellings"] == 10

def test_oral_tradition_fidelity():
    from lab.experiments.oral_tradition import OralTraditionEngine
    engine = OralTraditionEngine(seed=42)
    engine.create_story("s1", "t1", "perfect message")
    for _ in range(20):
        engine.tell("s1", "a", "b", corruption_rate=0.1)
    health = engine.tradition_health()
    assert health["avg_fidelity"] < 1.0

def test_sacred_geometry():
    from lab.experiments.sacred_geometry import SacredGeometryEngine
    engine = SacredGeometryEngine()
    engine.register_module("test", {"complexity": 5, "dependencies": 3, "size": 100})
    pattern = engine.generate_pattern("test")
    assert len(pattern.points) >= 6
    assert pattern.symmetry_order >= 3
    assert pattern.total_area > 0

def test_sacred_geometry_spiral():
    from lab.experiments.sacred_geometry import SacredGeometryEngine
    engine = SacredGeometryEngine()
    spiral = engine.generate_spiral(n=20)
    assert len(spiral) == 20
    metatron = engine.generate_metatron()
    assert len(metatron) == 13
    flower = engine.generate_flower(rings=2)
    assert len(flower) > 7

def test_wave93_all_demos():
    from lab.experiments.urban_legend_engine import demo as ul_demo
    from lab.experiments.alchemy_transmutation import demo as al_demo
    from lab.experiments.myth_generator import demo as mg_demo
    from lab.experiments.cargo_cult_detector import demo as cc_demo
    from lab.experiments.soup_of_life import demo as sl_demo
    from lab.experiments.language_drift import demo as ld_demo
    from lab.experiments.ritual_automation import demo as ra_demo
    from lab.experiments.folk_taxonomist import demo as ft_demo
    from lab.experiments.oral_tradition import demo as ot_demo
    from lab.experiments.sacred_geometry import demo as sg_demo
    for demo_fn in [ul_demo, al_demo, mg_demo, cc_demo, sl_demo,
                    ld_demo, ra_demo, ft_demo, ot_demo, sg_demo]:
        result = demo_fn()
        assert result is not None
