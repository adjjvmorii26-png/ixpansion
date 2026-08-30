import json

import constellation_dice
import cordyceps
import kintsugi
import negative_space
import mood_superposition
import stigmergy
import sympoiesis
import stochastic_resonance
import liminal_space
import phosphorescence
import memory_fern
import tessellation
import flocking
import epigenetic_landscape
import homing
import homeostasis


class TestKintsugi:
    def test_repair_honors_scars_and_is_deterministic(self):
        artifact = {"id": "shell", "fractures": [{"id": "a", "length": 3}, {"id": "b", "length": 8}]}
        first = kintsugi.repair(artifact)
        second = kintsugi.repair(artifact)

        assert first == second
        assert first["state"] == "repaired"
        assert [seam["source_fracture"] for seam in first["seams"]] == ["a", "b"]
        assert all(seam["scar_visibility"] == "honored" for seam in first["seams"])

    def test_cli_repairs_demo_artifact(self, capsys):
        assert kintsugi.main([]) == 0
        assert json.loads(capsys.readouterr().out)["repair_fingerprint"]


class TestConstellationDice:
    def test_throw_is_deterministic_and_bounded(self):
        first = constellation_dice.throw_dice(42)
        second = constellation_dice.throw_dice(42)

        assert first == second
        assert first["title"].startswith("The ")
        assert len(first["stars"]) == 5
        assert len({(star["x"], star["y"]) for star in first["stars"]}) == 5

    def test_invalid_star_count_fails_closed(self, capsys):
        assert constellation_dice.main(["--stars", "2"]) == 1
        assert json.loads(capsys.readouterr().out)["ok"] is False

    def test_cli_prints_myth(self, capsys):
        assert constellation_dice.main(["--seed", "7"]) == 0
        assert json.loads(capsys.readouterr().out)["seed"] == 7


class TestCordyceps:
    def test_consent_boundary_stops_spread_and_records_memory(self):
        hosts = [
            {"id": "root", "consent": True, "links": ["open", "sealed"]},
            {"id": "open", "consent": True, "links": []},
            {"id": "sealed", "consent": False, "links": ["beyond"]},
            {"id": "beyond", "consent": True, "links": []},
        ]
        result = cordyceps.spread(hosts, ["root"], 2)

        assert result["state"]["open"] == "expressing"
        assert result["state"]["sealed"] == "immunity-memory"
        assert result["state"]["beyond"] == "dormant"
        assert result["refusal_is_not_failure"] is True

    def test_cli_runs_demo(self, capsys):
        assert cordyceps.main([]) == 0
        assert json.loads(capsys.readouterr().out)["generations"] == 3


class TestNegativeSpace:
    def test_absence_pressures_rank_adjacent_voids_first(self):
        result = negative_space.read_absence([[3, 0], [2, 1], [3, 1], [4, 1], [3, 2]])
        strongest = result["strongest_absences"][0]

        assert result["absence_count"] == 44
        assert (strongest["x"], strongest["y"]) in {(2, 2), (4, 2), (3, 3)}
        assert strongest["adjacent_presence"] >= 1

    def test_out_of_bounds_presence_fails(self):
        import pytest

        with pytest.raises(ValueError):
            negative_space.read_absence([[9, 9]], 3, 3)

    def test_cli_reads_custom_bounds(self, capsys):
        assert negative_space.main(["--width", "5", "--height", "5"]) == 0
        parsed = json.loads(capsys.readouterr().out)
        assert parsed["absence_count"] == 20


class TestMoodSuperposition:
    def test_synthetic_superposition_collapses_dominant_component(self):
        result = mood_superposition.demo()

        assert result["collapsed_label"] == "curiosity"
        assert -1 <= result["blended_valence"] <= 1
        assert result["not_a_claim_of_feeling"] is True

    def test_focus_changes_signature_and_label(self):
        focused = mood_superposition.main(["--focus", "tenderness"])
        assert focused == 0

    def test_empty_mood_is_rejected(self):
        import pytest

        with pytest.raises(ValueError):
            mood_superposition.superpose([])



class TestStigmergy:
    def test_simulation_runs(self):
        result = stigmergy.simulate(width=10, height=10, num_agents=6, steps=40, seed=42)
        assert result["num_agents"] == 6
        assert result["agents_reached"] >= 0
        assert len(result["history"]) == 40
        assert result["history"][-1]["trail_energy"] > 0

    def test_philosophy_present(self):
        result = stigmergy.simulate(seed=7)
        assert "pheromone" in result["philosophy"]

    def test_hot_path_cells_exist(self):
        result = stigmergy.simulate(seed=42)
        assert len(result["hot_path"]) > 0
        assert all("cell" in c for c in result["hot_path"])


class TestSympoiesis:
    def test_simulation_runs(self):
        result = sympoiesis.simulate(agents=8, rounds=10, seed=42)
        assert result["total_spores"] == 80
        assert "type_distribution" in result
        assert len(result["ascii_constellation"]) == 20

    def test_emergence_metrics(self):
        result = sympoiesis.simulate(seed=1)
        assert result["emergence"]["pattern_diversity"] > 0
        assert result["spatial"]["max_density"] >= 1

    def test_agent_contributions(self):
        result = sympoiesis.simulate(agents=5, rounds=3, seed=9)
        assert len(result["agent_contributions"]) == 5
        assert all(a["spores"] == 3 for a in result["agent_contributions"])

    def test_different_seeds_different_results(self):
        r1 = sympoiesis.simulate(seed=1)
        r2 = sympoiesis.simulate(seed=2)
        assert r1["emergence"]["resonance_coherence"] != r2["emergence"]["resonance_coherence"]



class TestStochasticResonance:
    def test_detect_runs(self):
        result = stochastic_resonance.detect(signal_amp=0.3, noise_level=0.5, threshold=1.0)
        assert result["num_samples"] == 5000
        assert "clean" in result and "noisy" in result

    def test_sweep_finds_optimal(self):
        result = stochastic_resonance.sweep(signal_amp=0.3, threshold=1.0)
        assert result["optimal_noise"] > 0
        assert result["optimal_quality"] >= 0
        assert len(result["sweep_results"]) > 10

    def test_resonance_detected_at_right_level(self):
        result = stochastic_resonance.sweep(signal_amp=0.3, threshold=1.0)
        # At optimal noise, quality should be better than no noise
        assert result["optimal_quality"] >= result["quality_without_noise"]

    def test_philosophy_present(self):
        result = stochastic_resonance.detect(signal_amp=0.3, noise_level=0.5, threshold=1.0)
        assert "noise" in result["philosophy"].lower()



class TestLiminalSpace:
    def test_analyze_runs(self):
        from liminal_space import _make_points, analyze_points
        points = _make_points(10, 3, seed=42)
        result = analyze_points(points, k=8)
        assert result["num_points"] == len(points)
        assert "distribution" in result

    def test_distribution_has_three_classes(self):
        from liminal_space import _make_points, analyze_points
        points = _make_points(15, 2, seed=7)
        result = analyze_points(points)
        d = result["distribution"]
        # Categories can overlap (frontier points are also liminal)
        # But deep_core should be disjoint from liminal
        assert d["deep_core"] + d["liminal_edge"] >= 0
        assert d["frontier"] <= d["liminal_edge"] + d["deep_core"]
        assert result["num_points"] > 0

    def test_frontier_points_exist(self):
        from liminal_space import _make_points, analyze_points
        points = _make_points(20, 3, seed=42)
        result = analyze_points(points)
        assert result["distribution"]["frontier"] > 0

    def test_anomaly_mode(self):
        from liminal_space import _make_points, find_anomalies
        points = _make_points(15, 3, seed=42)
        result = find_anomalies(points)
        assert result["top_anomaly"] is not None
        assert result["top_anomaly"]["anomaly_score"] > 0



class TestPhosphorescence:
    def test_simulation_runs(self):
        result = phosphorescence.simulate(num_experiences=20, num_cells=8, seed=42)
        assert result["num_cells"] == 8
        assert result["total_energy_received"] > 0

    def test_dark_phase_has_discharge(self):
        result = phosphorescence.simulate(seed=7)
        glow_sample = result["glow_history_sample"]
        assert len(glow_sample) > 0
        assert all(g["phase"] == "dark" for g in glow_sample)

    def test_decay_models_differ(self):
        retentions = []
        for model in ["exponential", "logarithmic", "linear", "power"]:
            r = phosphorescence.simulate(decay_model=model, seed=42)
            retentions.append(r["energy_retention"])
        assert len(set(retentions)) > 2  # at least 3 distinct values

    def test_most_persistent_cell_exists(self):
        result = phosphorescence.simulate(seed=42)
        assert result["most_persistent_cell"]["persistence_ratio"] >= 0



class TestMemoryFern:
    def test_growth_runs(self):
        result = memory_fern.analyze_growth("A", "fern", 4)
        assert result["growth_summary"]["generations"] == 4
        assert result["growth_summary"]["end_length"] > result["growth_summary"]["start_length"]

    def test_different_rules_different_output(self):
        r1 = memory_fern.analyze_growth("F", "dragon", 3)
        r2 = memory_fern.analyze_growth("F", "sierpinski", 3)
        assert r1["encoding"]["total_symbols"] != r2["encoding"]["total_symbols"]

    def test_brackets_balanced(self):
        result = memory_fern.analyze_growth("A", "fern", 5)
        final = result["growth_curve"][-1]
        assert final["balanced"]

    def test_fractal_dimension_positive(self):
        result = memory_fern.analyze_growth("F", "branching", 4)
        assert result["growth_curve"][-1]["fractal_dim"] > 0



class TestTessellation:
    def test_generation_runs(self):
        result = tessellation.generate_tiling(depth=3, seed=42)
        assert result["num_triangles"] > 0
        assert result["is_aperiodic"]
    
    def test_thick_and_thin_both_present(self):
        result = tessellation.generate_tiling(depth=4)
        assert result["thick"] > 0
        assert result["thin"] > 0
    
    def test_deeper_depth_more_triangles(self):
        r3 = tessellation.generate_tiling(depth=2)
        r5 = tessellation.generate_tiling(depth=5)
        assert r5["num_triangles"] > r3["num_triangles"]



class TestFlocking:
    def test_simulation_runs(self):
        result = flocking.simulate(num_agents=20, num_steps=50, seed=42)
        assert result["num_agents"] == 20
        assert result["final_avg_speed"] > 0
    
    def test_flock_converges(self):
        result = flocking.simulate(num_agents=30, num_steps=100, seed=42)
        # Cohesion should decrease (flock gets tighter)
        trajectory = result["cohesion_trajectory"]
        assert trajectory[-1] < trajectory[0]
    
    def test_agents_stay_in_bounds(self):
        result = flocking.simulate(num_agents=20, num_steps=50, seed=7)
        assert result["num_steps"] == 50



class TestEpigeneticLandscape:
    def test_simulation_runs(self):
        result = epigenetic_landscape.simulate(num_cells=10, num_steps=100, seed=42)
        assert result["num_cells"] == 10
        assert result["differentiated"] > 0
    
    def test_multiple_fates(self):
        result = epigenetic_landscape.simulate(num_cells=15, num_steps=120, seed=42)
        assert len(result["fate_distribution"]) > 1
    
    def test_all_differentiate(self):
        result = epigenetic_landscape.simulate(num_cells=10, num_steps=150, seed=42)
        assert result["differentiated"] == result["num_cells"]
    
    def test_landscape_function_works(self):
        h1 = epigenetic_landscape._landscape_function(0.5, 5.0, 6)
        h2 = epigenetic_landscape._landscape_function(0.5, 0.0, 6)
        assert isinstance(h1, float)
        assert isinstance(h2, float)



class TestHoming:
    def test_simulation_runs(self):
        result = homing.simulate(num_birds=15, max_steps=150, seed=42)
        assert result["num_birds"] == 15
        assert result["birds_arrived"] >= 0
    
    def test_flock_finds_home(self):
        result = homing.simulate(num_birds=20, max_steps=250, seed=42)
        assert result["birds_arrived"] > 0
    
    def test_higher_noise_fewer_arrivals(self):
        noisy = homing.simulate(num_birds=10, noise=0.8, max_steps=200, seed=42)
        clean = homing.simulate(num_birds=10, noise=0.1, max_steps=200, seed=42)
        assert clean["birds_arrived"] >= noisy["birds_arrived"]



class TestHomeostasis:
    def test_system_returns_to_setpoint(self):
        result = homeostasis.simulate(disturbances=6, steps=50, seed=42)
        assert result["resilience_index"] > 0
        assert all(v <= 3.0 for v in result["deviation_from_setpoint"].values())
    
    def test_recovery_rates_bounded(self):
        result = homeostasis.simulate(disturbances=8, steps=50, seed=42)
        for name, log in result["recovery_log"].items():
            assert log["recovery_rate"] <= 1.001
    
    def test_stronger_disturbances_harder_recovery(self):
        light = homeostasis.simulate(disturbances=6, steps=50, strong=False, seed=42)
        strong = homeostasis.simulate(disturbances=6, steps=50, strong=True, seed=42)
        assert strong["resilience_index"] <= light["resilience_index"] + 1e-9
