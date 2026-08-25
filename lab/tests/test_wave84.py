from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

class TestSystemOrchestrator:
    def test_register_and_tick(self):
        from lab.system_orchestrator import SystemOrchestrator
        o = SystemOrchestrator(42)
        o.register_subsystem("test"); r = o.tick()
        assert r["tick"] == 1
    def test_simulate(self):
        from lab.system_orchestrator import SystemOrchestrator
        o = SystemOrchestrator(42)
        for n in ["a", "b", "c"]: o.register_subsystem(n)
        r = o.simulate(ticks=10)
        assert r["ticks"] == 10; assert r["total_events"] >= 0
    def test_demo(self):
        from lab.system_orchestrator import demo
        r = demo(); assert r["report"]["subsystems"] == 8

class TestIxpansionBridge:
    def test_mutation(self):
        from lab.ixpansion_bridge import IxpansionBridge
        b = IxpansionBridge(42)
        b.mesh.add_node("a", "worker"); b.mesh.add_node("b", "worker")
        b.mesh.auto_connect("star")
        r = b.tick()
        assert r["epoch"] == 1
    def test_simulate(self):
        from lab.ixpansion_bridge import IxpansionBridge
        b = IxpansionBridge(42)
        r = b.simulate(ticks=10)
        assert r["ticks"] == 10; assert r["total_mutations"] >= 0
    def test_demo(self):
        from lab.ixpansion_bridge import demo
        r = demo(); assert r["report"]["mesh_nodes"] >= 5

class TestCodebaseGenome:
    def test_demo(self):
        from lab.experiments.codebase_genome import demo
        r = demo(); assert r["chromosomes"] > 0; assert r["fitness"] > 0

class TestPropagationField:
    def test_demo(self):
        from lab.experiments.propagation_field import demo
        r = demo(); assert r["sources"] == 5; assert r["dynamic_range"] > 0

class TestSystemMetabolism:
    def test_demo(self):
        from lab.experiments.system_metabolism import demo
        r = demo(); assert r["cycles"] == 10; assert 0 < r["health"] <= 1

class TestFractalDimensionCounter:
    def test_demo(self):
        from lab.experiments.fractal_dimension_counter import demo
        r = demo(); assert r["dimension"] > 0; assert r["point_count"] == 100

class TestEntropicPressureGauge:
    def test_demo(self):
        from lab.experiments.entropic_pressure_gauge import demo
        r = demo(); assert r["readings"] == 4; assert r["avg_pressure"] > 0

class TestAgentDreamJournal:
    def test_demo(self):
        from lab.experiments.agent_dream_journal import demo
        r = demo(); assert r["analysis"]["total_dreams"] == 16
