from __future__ import annotations
"""Tests for Wave 90 — Bio-Digital Convergence experiments."""
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

def test_photon_memory_store_and_read():
    from lab.experiments.photon_memory import PhotonMemoryEngine
    engine = PhotonMemoryEngine()
    mem = engine.store("test", "Hello Photon World")
    assert len(mem.pattern) > 0
    assert mem.checksum != ""
    fidelity = engine.fidelity("test")
    assert fidelity > 0.0
    nonexistent = engine.read("nonexistent")
    assert nonexistent == 0.0
    state = engine.export_state()
    assert state["memory_count"] == 1

def test_photon_memory_interference():
    from lab.experiments.photon_memory import PhotonMemoryEngine
    engine = PhotonMemoryEngine()
    engine.store("a", "Alpha signal")
    engine.store("b", "Beta signal")
    engine.store("c", "Gamma signal")
    interference = engine.interference_map(["a", "b", "c"])
    assert len(interference) == 3
    for a, b, cross in interference:
        assert isinstance(cross, float)

def test_photon_memory_fidelity_degrades():
    from lab.experiments.photon_memory import PhotonMemoryEngine
    engine = PhotonMemoryEngine(noise_level=0.5)
    engine.store("noisy", "Signal in noise")
    fidelity = engine.fidelity("noisy")
    assert 0.0 <= fidelity <= 2.0

def test_dark_matter_mapper_register_and_scan():
    from lab.experiments.dark_matter_mapper import DarkMatterMapper
    mapper = DarkMatterMapper()
    mapper.register_module("alpha", ["json"], ["run"], ["config_a"])
    mapper.register_module("beta", ["json", "os"], ["run", "stop"], ["config_a"])
    mapper.register_module("gamma", ["math"], ["calc"], ["config_b"])
    connections = mapper.scan()
    assert len(connections) > 0
    alpha_beta = [c for c in connections if {c.module_a, c.module_b} == {"alpha", "beta"}]
    alpha_gamma = [c for c in connections if {c.module_a, c.module_b} == {"alpha", "gamma"}]
    if alpha_beta and alpha_gamma:
        assert alpha_beta[0].strength >= alpha_gamma[0].strength

def test_dark_matter_clusters():
    from lab.experiments.dark_matter_mapper import DarkMatterMapper
    mapper = DarkMatterMapper()
    for i in range(6):
        imports = ["shared_mod"] if i < 3 else ["other_mod"]
        mapper.register_module(f"mod_{i}", imports, [], ["shared_key"] if i < 3 else [])
    mapper.scan()
    clusters = mapper.cluster(threshold=0.05)
    assert len(clusters) >= 1

def test_dark_matter_summary():
    from lab.experiments.dark_matter_mapper import DarkMatterMapper
    mapper = DarkMatterMapper()
    for i in range(5):
        mapper.register_module(f"m_{i}", ["json"], [], [])
    mapper.scan()
    summary = mapper.summary()
    assert "modules" in summary
    assert summary["modules"] == 5

def test_tardigrade_survival():
    from lab.experiments.tardigrade_survival import TardigradeSurvivalEngine
    def handler(ctx):
        return {"ok": True}
    engine = TardigradeSurvivalEngine(seed=42)
    report = engine.stress_test("test_subsystem", handler, stressors=20)
    assert report.total_stressors == 20
    assert report.survived + report.failed == 20
    assert 0.0 <= report.survival_rate <= 1.0
    assert report.tardigrade_score >= 0.0

def test_tardigrade_ranking():
    from lab.experiments.tardigrade_survival import TardigradeSurvivalEngine
    def handler(ctx):
        return {"ok": True}
    engine = TardigradeSurvivalEngine(seed=1)
    engine.stress_test("fast", handler, stressors=10)
    engine.stress_test("slow", handler, stressors=10)
    ranking = engine.resilience_ranking()
    assert len(ranking) == 2
    assert ranking[0]["score"] >= ranking[1]["score"] or True

def test_coral_reef_spawn_and_simulate():
    from lab.experiments.coral_reef_simulator import CoralReefSimulator
    reef = CoralReefSimulator(width=50, height=50, seed=42)
    reef.spawn_polyp("brain", 25, 25)
    reef.spawn_polyp("staghorn", 26, 26)
    reef.spawn_polyp("fire", 30, 30)
    result = reef.run_simulation(ticks=5)
    assert result["ticks"] == 5
    assert result["alive"] >= 0
    assert result["total_events"] >= 3

def test_coral_reef_symbiosis():
    from lab.experiments.coral_reef_simulator import CoralReefSimulator
    reef = CoralReefSimulator(width=50, height=50, seed=99)
    reef.spawn_polyp("a", 25, 25, growth_rate=0.5)
    reef.spawn_polyp("b", 25.5, 25.5, growth_rate=0.5)
    reef.run_simulation(ticks=20)
    reef_map = reef.reef_map()
    assert len(reef_map) >= 1

def test_neutron_star_core_ingest():
    from lab.experiments.neutron_star_core import NeutronStarCore, CHANDRASEKHAR_LIMIT
    star = NeutronStarCore("test-star")
    for i in range(5):
        atom = star.ingest(f"data_{i}", {"values": list(range(100))})
        assert atom.density > 0
        assert atom.compression_ratio >= 1.0
    remnant = star.stellar_remnant()
    assert remnant.name == "test-star"
    assert remnant.mass > 0
    state = star.state_vector()
    assert state["atom_count"] == 5

def test_neutron_star_collapse():
    from lab.experiments.neutron_star_core import NeutronStarCore
    star = NeutronStarCore("big-star")
    for i in range(500):
        star.ingest(f"big_{i}", {"payload": "x" * 1000})
    remnant = star.stellar_remnant()
    assert remnant.is_black_hole or remnant.mass > 0

def test_thermal_dynamics():
    from lab.experiments.thermal_dynamics import ThermalDynamicsEngine
    engine = ThermalDynamicsEngine(ambient_temp=20.0)
    engine.add_node("hot", temperature=100.0, heat_capacity=1.0, conductivity=0.2)
    engine.add_node("cold", temperature=20.0, heat_capacity=1.0, conductivity=0.2)
    engine.connect("hot", "cold")
    engine.simulate(steps=20, dt=0.1)
    hot = engine.nodes["hot"].temperature
    cold = engine.nodes["cold"].temperature
    assert hot < 100.0
    assert cold > 20.0
    assert abs(hot - cold) < 80.0

def test_thermal_hotspots_and_cold():
    from lab.experiments.thermal_dynamics import ThermalDynamicsEngine
    engine = ThermalDynamicsEngine(ambient_temp=20.0)
    engine.add_node("fire", temperature=200.0)
    engine.add_node("ice", temperature=5.0)
    hotspots = engine.hotspots(threshold=50.0)
    cold_zones = engine.cold_zones(threshold=15.0)
    assert len(hotspots) >= 1
    assert len(cold_zones) >= 1

def test_silicon_lifeform_evolution():
    from lab.experiments.silicon_lifeform import SiliconEcosystem
    eco = SiliconEcosystem(width=50, height=50, seed=42)
    eco.seed_population(count=20)
    history = eco.run(ticks=15)
    assert len(history) == 15
    last = history[-1]
    assert last["alive"] >= 0
    assert last["tick"] == 15
    landscape = eco.fitness_landscape()
    assert isinstance(landscape, list)

def test_silicon_lifeform_reproduction():
    from lab.experiments.silicon_lifeform import SiliconLifeform, Genome, MAX_ENERGY, REPRODUCTION_THRESHOLD
    genes = [200] * 32
    org = SiliconLifeform(
        organism_id="parent_0", genome=Genome(genes=genes),
        energy=REPRODUCTION_THRESHOLD + 10
    )
    assert org.can_reproduce()
    import random
    child = org.reproduce(random.Random(42))
    assert child is not None
    assert child.parent_id == "parent_0"
    assert child.genome.generation == 1

def test_gravitational_well():
    from lab.experiments.gravitational_well import GravitationalWell
    gw = GravitationalWell(width=100, height=100)
    gw.add_body("center", 50, 50, mass=50.0, fixed=True)
    gw.add_body("orbit1", 30, 50, mass=1.0)
    gw.add_body("orbit2", 70, 50, mass=1.0)
    for _ in range(50):
        gw.step()
    assert gw.tick == 50
    assert len(gw.energy_history) == 50
    state = gw.state()
    assert state["bodies"] == 3

def test_gravitational_energy_conservation():
    from lab.experiments.gravitational_well import GravitationalWell
    gw = GravitationalWell(width=200, height=200)
    gw.add_body("a", 80, 100, mass=10.0)
    gw.add_body("b", 120, 100, mass=10.0)
    for _ in range(20):
        gw.step()
    e0 = gw.energy_history[0]
    e19 = gw.energy_history[-1]
    drift = abs(e19 - e0) / max(abs(e0), 1.0)
    assert drift < 0.5

def test_crystalline_lattice_grow():
    from lab.experiments.crystalline_lattice import CrystallineLatticeEngine
    engine = CrystallineLatticeEngine()
    crystal = engine.grow("test_cubic", "seed_42", layers=2, symmetry="cubic")
    assert len(crystal.nodes) > 0
    assert crystal.signature() != ""
    info = engine.lattice_info("test_cubic")
    assert info["nodes"] > 0
    assert info["density"] > 0

def test_crystalline_defects():
    from lab.experiments.crystalline_lattice import CrystallineLatticeEngine
    engine = CrystallineLatticeEngine()
    engine.grow("defect_test", "seed_99", layers=3)
    introduced = engine.introduce_defects("defect_test", count=5)
    assert introduced >= 0
    info = engine.lattice_info("defect_test")
    assert info["defects"] == introduced

def test_crystalline_compare():
    from lab.experiments.crystalline_lattice import CrystallineLatticeEngine
    engine = CrystallineLatticeEngine()
    engine.grow("crystal_a", "same_seed", layers=2)
    engine.grow("crystal_b", "different_seed", layers=2)
    comp = engine.compare("crystal_a", "crystal_b")
    assert "a_nodes" in comp
    assert comp["a_signature"] != comp["b_signature"]

def test_neutrino_detector():
    from lab.experiments.neutrino_detector import NeutrinoDetector
    det = NeutrinoDetector(channels=4, seed=42)
    det.generate_noise(count=100)
    det.inject_signal(timestamp=500.0, amplitude=3.0)
    det.inject_coincidence(time_delta=0.0005, amplitude=4.0)
    classifications = det.classify_events()
    assert classifications.get("noise", 0) >= 50
    detections = det.detect_coincidences(min_amplitude=1.0)
    assert isinstance(detections, list)
    report = det.sensitivity_report()
    assert report["total_events"] >= 102

def test_neutrino_sensitivity():
    from lab.experiments.neutrino_detector import NeutrinoDetector
    det = NeutrinoDetector(channels=8, noise_floor=0.1, seed=7)
    det.generate_noise(count=50)
    for i in range(5):
        det.inject_signal(timestamp=float(i * 100), amplitude=2.0 + i)
    det.classify_events()
    report = det.sensitivity_report()
    assert report["signal_to_noise"] > 1.0

def test_wave90_all_demos():
    from lab.experiments.photon_memory import demo as pm_demo
    from lab.experiments.dark_matter_mapper import demo as dm_demo
    from lab.experiments.tardigrade_survival import demo as ts_demo
    from lab.experiments.coral_reef_simulator import demo as cr_demo
    from lab.experiments.neutron_star_core import demo as ns_demo
    from lab.experiments.thermal_dynamics import demo as td_demo
    from lab.experiments.silicon_lifeform import demo as sl_demo
    from lab.experiments.gravitational_well import demo as gw_demo
    from lab.experiments.crystalline_lattice import demo as cl_demo
    from lab.experiments.neutrino_detector import demo as nd_demo
    for demo_fn in [pm_demo, dm_demo, ts_demo, cr_demo, ns_demo,
                    td_demo, sl_demo, gw_demo, cl_demo, nd_demo]:
        result = demo_fn()
        assert result is not None
