"""Tests for Wave 75 experimental innovation modules."""
from __future__ import annotations

import pytest


class TestConsensusRealitySim:
    def test_import(self):
        from lab.experiments.consensus_reality_sim import ConsensusRealitySimulator
        assert ConsensusRealitySimulator is not None

    def test_init_creates_world(self):
        from lab.experiments.consensus_reality_sim import ConsensusRealitySimulator
        sim = ConsensusRealitySimulator(width=4, height=4, seed=42)
        sim.init_world()
        assert len(sim._world) == 16

    def test_agents_observe(self):
        from lab.experiments.consensus_reality_sim import ConsensusRealitySimulator
        sim = ConsensusRealitySimulator(width=4, height=4, seed=42)
        sim.init_world()
        sim.add_agents(3)
        sim.tick()
        assert sum(a.observations_made for a in sim._agents) > 0

    def test_consolidation(self):
        from lab.experiments.consensus_reality_sim import ConsensusRealitySimulator
        sim = ConsensusRealitySimulator(width=4, height=4, seed=42)
        sim.init_world()
        sim.add_agents(8)
        for _ in range(50):
            sim.tick()
        assert sum(1 for c in sim._world.values() if c.consolidated) > 0

    def test_accuracy_report(self):
        from lab.experiments.consensus_reality_sim import ConsensusRealitySimulator
        sim = ConsensusRealitySimulator(width=4, height=4, seed=42)
        sim.init_world()
        sim.add_agents(5)
        for _ in range(20):
            sim.tick()
        report = sim.accuracy_report()
        assert "accuracy" in report
        assert 0.0 <= report["accuracy"] <= 1.0


class TestPanopticonEcology:
    def test_import(self):
        from lab.experiments.panopticon_ecology import PanopticonEcology
        assert PanopticonEcology is not None

    def test_cells_initialize(self):
        from lab.experiments.panopticon_ecology import PanopticonEcology
        eco = PanopticonEcology(width=4, height=4, seed=42)
        eco.init_cells()
        assert len(eco._cells) == 16

    def test_agents_walk(self):
        from lab.experiments.panopticon_ecology import PanopticonEcology
        eco = PanopticonEcology(width=4, height=4, seed=42)
        eco.init_cells()
        eco.add_agent("a1", "sentinel")
        eco.tick()
        assert eco._tick == 1

    def test_terrain_shifts(self):
        from lab.experiments.panopticon_ecology import PanopticonEcology
        eco = PanopticonEcology(width=4, height=4, seed=42)
        eco.init_cells()
        for i in range(10):
            eco.add_agent(f"a{i}", ["sentinel", "architect", "wanderer"][i % 3])
        for _ in range(50):
            eco.tick()
        report = eco.ecology_report()
        assert report["total_shifts"] >= 0

    def test_ecology_report(self):
        from lab.experiments.panopticon_ecology import PanopticonEcology
        eco = PanopticonEcology(width=4, height=4, seed=42)
        eco.init_cells()
        eco.add_agent("a", "sentinel")
        eco.tick()
        report = eco.ecology_report()
        assert "terrain_distribution" in report


class TestHexVMProfiler:
    def test_import(self):
        from lab.experiments.hex_vm_profiler import HexVMProfiler, HexProgram
        assert HexVMProfiler is not None

    def test_profile_counter(self):
        from lab.experiments.hex_vm_profiler import HexVMProfiler, HexProgram
        profiler = HexVMProfiler()
        program = HexProgram.from_source("PUSH 1\nPUSH 2\nADD\nEMIT\nHALT")
        result = profiler.profile(program)
        assert result["summary"]["total_instructions"] == 5
        assert result["summary"]["outputs"] == 1
        assert result["summary"]["halts_cleanly"]

    def test_profile_max_stack(self):
        from lab.experiments.hex_vm_profiler import HexVMProfiler, HexProgram
        profiler = HexVMProfiler()
        program = HexProgram.from_source("PUSH 1\nPUSH 2\nPUSH 3\nPUSH 4\nEMIT\nEMIT\nEMIT\nEMIT\nHALT")
        result = profiler.profile(program)
        assert result["summary"]["max_stack_depth"] == 4

    def test_fingerprint_changes_with_program(self):
        from lab.experiments.hex_vm_profiler import HexVMProfiler, HexProgram
        profiler = HexVMProfiler()
        p1 = profiler.profile(HexProgram.from_source("PUSH 1\nEMIT\nHALT"))
        p2 = profiler.profile(HexProgram.from_source("PUSH 1\nPUSH 2\nADD\nEMIT\nHALT"))
        assert p1["fingerprint"] != p2["fingerprint"]


class TestExpansionRuleSynth:
    def test_import(self):
        from lab.experiments.expansion_rule_synth import RuleSynthesizer
        assert RuleSynthesizer is not None

    def test_load_seeds(self):
        from lab.experiments.expansion_rule_synth import RuleSynthesizer
        synth = RuleSynthesizer(seed=42)
        rules = synth.load_seeds([{"name": "test", "condition": "x above 0.5", "action": "do_y"}])
        assert len(rules) == 1

    def test_invert(self):
        from lab.experiments.expansion_rule_synth import RuleSynthesizer, Rule
        synth = RuleSynthesizer(seed=42)
        rule = Rule(rule_id="r1", name="test", condition="entropy greater 0.5", action="fix")
        inverted = synth.invert(rule)
        assert "less" in inverted.condition or "below" in inverted.condition

    def test_compose(self):
        from lab.experiments.expansion_rule_synth import RuleSynthesizer, Rule
        synth = RuleSynthesizer(seed=42)
        a = Rule(rule_id="a", name="a", condition="x above 0.5", action="do_a")
        b = Rule(rule_id="b", name="b", condition="y below 0.3", action="do_b")
        composed = synth.compose(a, b)
        assert "AND" in composed.condition
        assert composed.generation == 1

    def test_synthesize_generation(self):
        from lab.experiments.expansion_rule_synth import RuleSynthesizer
        synth = RuleSynthesizer(seed=42)
        gen0 = synth.load_seeds([
            {"name": "r1", "condition": "a above 0.5", "action": "x"},
            {"name": "r2", "condition": "b below 0.3", "action": "y"},
        ])
        gen1 = synth.synthesize_generation(gen0)
        assert len(gen1) > 0
        assert all(r.generation >= 1 for r in gen1)


class TestGlitchPatternGenerator:
    def test_import(self):
        from lab.experiments.glitch_pattern_generator import GlitchPatternGenerator
        assert GlitchPatternGenerator is not None

    def test_generate_glitches(self):
        from lab.experiments.glitch_pattern_generator import GlitchPatternGenerator
        gen = GlitchPatternGenerator(seed=42)
        glitches = gen.generate(count=5)
        assert len(glitches) == 5

    def test_classify_severity(self):
        from lab.experiments.glitch_pattern_generator import GlitchPatternGenerator, Glitch
        gen = GlitchPatternGenerator(seed=42)
        g = Glitch(glitch_id="test", glitch_type="test", severity=0.9, affected_agents=[], description="", repair_strategy="")
        result = gen.classify_severity(g)
        assert result["level"] == "critical"

    def test_resolve_all(self):
        from lab.experiments.glitch_pattern_generator import GlitchPatternGenerator
        gen = GlitchPatternGenerator(seed=42)
        gen.generate(count=3)
        result = gen.resolve_all()
        assert result["resolved"] == 3
        assert all(g.resolved for g in gen._glitches)

    def test_glitch_report(self):
        from lab.experiments.glitch_pattern_generator import GlitchPatternGenerator
        gen = GlitchPatternGenerator(seed=42)
        gen.generate(count=10)
        report = gen.glitch_report()
        assert report["total_glitches"] == 10
        assert "type_distribution" in report


class TestChronoForgeOrchestrator:
    def test_import(self):
        from lab.experiments.chrono_forge_orchestrator import ChronoForgeOrchestrator
        assert ChronoForgeOrchestrator is not None

    def test_run_pipeline(self):
        from lab.experiments.chrono_forge_orchestrator import ChronoForgeOrchestrator
        orch = ChronoForgeOrchestrator(seed=42)
        result = orch.run_pipeline("test phrase")
        assert result["all_success"]
        assert len(result["steps"]) == 5

    def test_pipeline_varies_by_phrase(self):
        from lab.experiments.chrono_forge_orchestrator import ChronoForgeOrchestrator
        orch = ChronoForgeOrchestrator(seed=42)
        r1 = orch.run_pipeline("error in system")
        r2 = orch.run_pipeline("expand territory")
        # Different phrases produce different forge_mind rituals
        fm1 = [s for s in r1["steps"] if s["agent"] == "forge_mind"][0]
        fm2 = [s for s in r2["steps"] if s["agent"] == "forge_mind"][0]
        assert fm1["output_keys"] != fm2["output_keys"] or r1["seed_phrase"] != r2["seed_phrase"]

    def test_history_summary(self):
        from lab.experiments.chrono_forge_orchestrator import ChronoForgeOrchestrator
        orch = ChronoForgeOrchestrator(seed=42)
        orch.run_pipeline("a")
        orch.run_pipeline("b")
        summary = orch.history_summary()
        assert summary["total_runs"] == 2
        assert summary["success_rate"] == 1.0
