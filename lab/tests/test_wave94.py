from __future__ import annotations
"""Tests for Wave 94 — Digital Ecology experiments."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

def test_keystone_species():
    from lab.experiments.keystone_species import KeystoneDetector
    d = KeystoneDetector()
    d.add_module("a", dependents=["b", "c"], dependencies=[])
    d.add_module("b", dependents=["d"], dependencies=["a"])
    d.add_module("c", dependents=[], dependencies=["a"])
    d.add_module("d", dependents=[], dependencies=["b"])
    top = d.top_keystone(2)
    assert len(top) == 2
    assert top[0]["criticality"] > 0

def test_symbiosis_network():
    from lab.experiments.symbiosis_network import SymbiosisNetwork
    net = SymbiosisNetwork()
    net.register("a", provides=["x"], consumes=["y"])
    net.register("b", provides=["y"], consumes=["x"])
    net.register("c", provides=[], consumes=["x", "y"])
    net.analyze()
    report = net.report()
    assert report["modules"] == 3
    assert report["relations"] >= 1

def test_invasive_species():
    from lab.experiments.invasive_species_detector import InvasiveSpeciesDetector
    d = InvasiveSpeciesDetector()
    d.register("normal", 3, 500, 10)
    d.register("invasive", 20, 5000, 100)
    d.set_baseline("normal", 450)
    d.set_baseline("invasive", 300)
    invasive = d.detect()
    assert len(invasive) >= 1
    assert invasive[0].name == "invasive"

def test_ecosystem_services():
    from lab.experiments.ecosystem_services import EcosystemServices
    eco = EcosystemServices()
    eco.register("auth", {"authentication": 0.9})
    eco.register("cache", {"caching": 0.8})
    ranking = eco.ranking()
    assert len(ranking) == 2
    assert ranking[0]["value"] > 0

def test_biomimetic_optimizer():
    from lab.experiments.biomimetic_optimizer import BiomimeticOptimizer
    opt = BiomimeticOptimizer(dimensions=2, pop_size=10, seed=42)
    history = opt.optimize(objective="ackley", iterations=20)
    assert len(history) == 20
    assert opt.best_fitness < 15.0

def test_extinction_debt():
    from lab.experiments.extinction_debt import ExtinctionDebtAnalyzer
    a = ExtinctionDebtAnalyzer()
    a.register("healthy", [0.9, 0.85, 0.88, 0.9, 0.87])
    a.register("doomed", [0.8, 0.6, 0.4, 0.2, 0.05])
    report = a.report()
    assert report["total"] == 2
    assert "doomed" in report["statuses"]

def test_pollination_network():
    from lab.experiments.pollination_network import PollinationNetwork
    pn = PollinationNetwork()
    pn.register("a", ["idea1"])
    pn.register("b", [])
    pn.pollinate("a", "b", "idea1")
    report = pn.report()
    assert report["total_events"] == 1

def test_trophic_cascade():
    from lab.experiments.trophic_cascade import TrophicCascadeSimulator
    sim = TrophicCascadeSimulator()
    sim.add_module("predator", 0, [], 1.0)
    sim.add_module("prey", 1, ["predator"], 1.0)
    sim.add_module("plant", 2, ["prey"], 1.0)
    effects = sim.trigger_cascade("predator", -0.5)
    assert len(effects) >= 1
    assert effects[0]["new_health"] < 1.0

def test_edge_of_chaos():
    from lab.experiments.edge_of_chaos import EdgeOfChaosFinder
    finder = EdgeOfChaosFinder(grid_size=10, seed=42)
    result = finder.find_edge(rules=[30, 110], steps=10)
    assert result["best_rule"] in [30, 110]
    assert result["best_complexity"] > 0

def test_bioacoustic_monitor():
    from lab.experiments.bioacoustic_monitor import BioacousticMonitor
    m = BioacousticMonitor(seed=42)
    for _ in range(20):
        m.record_event("mod", "tick", amplitude=1.0)
    m.record_event("rogue", "CRASH", amplitude=5.0)
    anomalies = m.detect_anomalies(window=10)
    health = m.soundscape_health()
    assert health["total_events"] == 21

def test_wave94_all_demos():
    from lab.experiments.keystone_species import demo as ks_demo
    from lab.experiments.symbiosis_network import demo as sn_demo
    from lab.experiments.invasive_species_detector import demo as isd_demo
    from lab.experiments.ecosystem_services import demo as es_demo
    from lab.experiments.biomimetic_optimizer import demo as bo_demo
    from lab.experiments.extinction_debt import demo as ed_demo
    from lab.experiments.pollination_network import demo as pn_demo
    from lab.experiments.trophic_cascade import demo as tc_demo
    from lab.experiments.edge_of_chaos import demo as eoc_demo
    from lab.experiments.bioacoustic_monitor import demo as bam_demo
    for demo_fn in [ks_demo, sn_demo, isd_demo, es_demo, bo_demo,
                    ed_demo, pn_demo, tc_demo, eoc_demo, bam_demo]:
        result = demo_fn()
        assert result is not None
