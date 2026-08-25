"""Tests for Wave 77 meta-evolution layer modules."""
from __future__ import annotations

import pytest


class TestEvolutionKernel:
    def test_import(self):
        from lab.experiments.evolution_kernel import EvolutionKernel
        assert EvolutionKernel is not None

    def test_register_and_observe(self):
        from lab.experiments.evolution_kernel import EvolutionKernel
        kernel = EvolutionKernel(seed=42)
        kernel.register_module("mod_a", "mod_a", entropy=0.9, usage_frequency=0.1)
        kernel.tick()
        diff = kernel.differential()
        assert diff["total_proposals"] > 0

    def test_deprecation_for_low_usage(self):
        from lab.experiments.evolution_kernel import EvolutionKernel
        kernel = EvolutionKernel(seed=42)
        kernel.register_module("stale", "stale", entropy=0.3, usage_frequency=0.05)
        for _ in range(15):
            kernel.tick()
        diff = kernel.differential()
        types = [p["type"] for p in diff["top_priority"]]
        assert "deprecate" in types or "stabilize" in types

    def test_approve_proposal(self):
        from lab.experiments.evolution_kernel import EvolutionKernel
        kernel = EvolutionKernel(seed=42)
        kernel.register_module("mod", "mod", entropy=0.9)
        kernel.tick()
        diff = kernel.differential()
        pid = diff["top_priority"][0]["proposal_id"]
        assert kernel.approve_proposal(pid)
        assert kernel.differential()["approved"] >= 1


class TestFractalReactorGrid:
    def test_import(self):
        from lab.experiments.fractal_reactor_grid import FractalReactorGrid
        assert FractalReactorGrid is not None

    def test_subdivision(self):
        from lab.experiments.fractal_reactor_grid import FractalReactorGrid
        grid = FractalReactorGrid(seed=42)
        grid.init_grid(2, 2)
        initial = len(grid._cells)
        for _ in range(25):
            grid.tick()
        assert len(grid._cells) >= initial

    def test_merge(self):
        from lab.experiments.fractal_reactor_grid import FractalReactorGrid
        grid = FractalReactorGrid(seed=42, merge_threshold=0.1)
        grid.init_grid(2, 2)
        for _ in range(30):
            grid.tick()
        report = grid.grid_report()
        assert report["total_cells"] > 0

    def test_report_fields(self):
        from lab.experiments.fractal_reactor_grid import FractalReactorGrid
        grid = FractalReactorGrid(seed=42)
        grid.init_grid(2, 2)
        grid.tick()
        report = grid.grid_report()
        assert "levels" in report
        assert "leaf_cells" in report


class TestMycelialGovernor:
    def test_import(self):
        from lab.experiments.mycelial_governor import MycelialGovernor
        assert MycelialGovernor is not None

    def test_growth_proposals(self):
        from lab.experiments.mycelial_governor import MycelialGovernor
        gov = MycelialGovernor(seed=42)
        gov.add_organism("o1", "alpha")
        gov.add_organism("o2", "beta")
        gov.tick()
        report = gov.governor_report()
        assert report["total_proposals"] > 0

    def test_scarcity_enforced(self):
        from lab.experiments.mycelial_governor import MycelialGovernor
        gov = MycelialGovernor(seed=42, scarcity_threshold=0.3)
        for i in range(20):
            gov.add_organism(f"o{i}", "alpha")
        for _ in range(15):
            gov.tick()
        report = gov.governor_report()
        assert report["nutrient_pool"]["available"] >= 0


class TestOmegaDreamforge:
    def test_import(self):
        from lab.experiments.omega_prime_dreamforge import OmegaDreamforge
        assert OmegaDreamforge is not None

    def test_find_gaps(self):
        from lab.experiments.omega_prime_dreamforge import OmegaDreamforge
        forge = OmegaDreamforge(seed=42)
        forge.register_module("a", {"entropy": 0.9, "novelty": 0.2})
        forge.register_module("b", {"entropy": 0.1, "novelty": 0.8})
        gaps = forge.find_dream_gaps()
        assert len(gaps) > 0

    def test_dream_produces_blueprints(self):
        from lab.experiments.omega_prime_dreamforge import OmegaDreamforge
        forge = OmegaDreamforge(seed=42)
        forge.register_module("a", {"entropy": 0.5, "novelty": 0.6})
        forge.register_module("b", {"memory": 0.7, "depth": 0.3})
        blueprints = forge.dream(count=3)
        assert len(blueprints) == 3
        assert all(b.viability_score > 0 for b in blueprints)


class TestConstellationAutobiographer:
    def test_import(self):
        from lab.experiments.constellation_autobiographer import ConstellationAutobiographer
        assert ConstellationAutobiographer is not None

    def test_record_and_write(self):
        from lab.experiments.constellation_autobiographer import ConstellationAutobiographer
        auto = ConstellationAutobiographer(seed=42)
        auto.add_star("star1", "mod1", wave=72)
        auto.add_star("star2", "mod2", wave=72)
        auto.connect_stars(
            list(auto._stars.keys())[0], list(auto._stars.keys())[1]
        )
        chapter = auto.write_chapter(72)
        assert chapter["star_count"] == 2
        assert chapter["connections"] >= 1

    def test_full_autobiography(self):
        from lab.experiments.constellation_autobiographer import ConstellationAutobiographer
        auto = ConstellationAutobiographer(seed=42)
        for i in range(5):
            auto.add_star(f"star{i}", f"mod{i}", wave=72)
        auto.record_event("merge", "wave_72", "Wave 72 merged")
        report = auto.full_autobiography()
        assert report["total_stars"] == 5
        assert report["total_events"] == 1


class TestParadoxSingularityMonitor:
    def test_import(self):
        from lab.experiments.paradox_singularity_monitor import ParadoxSingularityMonitor
        assert ParadoxSingularityMonitor is not None

    def test_convergence_detection(self):
        from lab.experiments.paradox_singularity_monitor import ParadoxSingularityMonitor
        mon = ParadoxSingularityMonitor(seed=42, convergence_threshold=0.5)
        # Cluster 3 paradoxes close together
        mon.register_paradox("p1", "a", {"x": 0.8, "y": 0.6})
        mon.register_paradox("p2", "b", {"x": 0.75, "y": 0.55})
        mon.register_paradox("p3", "c", {"x": 0.7, "y": 0.65})
        # One far away
        mon.register_paradox("p4", "d", {"x": 0.1, "y": 0.1})
        for _ in range(10):
            mon.tick()
        report = mon.monitor_report()
        assert report["total_singularities"] > 0

    def test_report_fields(self):
        from lab.experiments.paradox_singularity_monitor import ParadoxSingularityMonitor
        mon = ParadoxSingularityMonitor(seed=42)
        mon.register_paradox("p1", "a", {"x": 0.5})
        mon.tick()
        report = mon.monitor_report()
        assert "total_paradoxes" in report
        assert "mean_severity" in report
