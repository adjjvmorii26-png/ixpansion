from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

class TestReactorBridge:
    def test_chaos_inject(self):
        from lab.reactor_bridge import ChaosReactor
        r = ChaosReactor(42)
        result = r.inject({"a": 1.0, "b": 0.5})
        assert "a" in result
    def test_pipeline(self):
        from lab.reactor_bridge import ReactorBridge
        b = ReactorBridge(42)
        result = b.apply_pipeline({"x": 1.0, "y": 0.5}, ["chaos", "order"])
        assert "x" in result
    def test_full_cycle(self):
        from lab.reactor_bridge import ReactorBridge
        b = ReactorBridge(42)
        result = b.full_cycle({"a": 0.8, "b": 0.3})
        assert "a" in result
    def test_demo(self):
        from lab.reactor_bridge import demo
        r = demo(); assert "pipeline" in r; assert "report" in r

class TestKernelBridge:
    def test_state_core(self):
        from lab.kernel_bridge import StateCore
        s = StateCore({"x": 1}); s.set("x", 2)
        assert s.get("x") == 2; assert s.history_length == 1
    def test_time_crystal(self):
        from lab.kernel_bridge import TimeCrystal
        tc = TimeCrystal(period=3)
        for i in range(6): tc.pulse({"a": {"pos": i}})
        assert len(tc.echoes) >= 1
    def test_entanglement(self):
        from lab.kernel_bridge import EntanglementManager
        e = EntanglementManager(42); e.entangle("a", "b", 0.9)
        assert e.correlate("a", "b") == 0.9
    def test_paradox_solver(self):
        from lab.kernel_bridge import ParadoxSolver
        ps = ParadoxSolver(); ps.register("a", "b", 0.6, 0.7)
        r = ps.resolve(); assert len(r) == 1
    def test_simulate(self):
        from lab.kernel_bridge import KernelBridge
        b = KernelBridge(42); r = b.simulate(ticks=10)
        assert r["ticks"] == 10; assert r["final_epoch"] == 10
    def test_demo(self):
        from lab.kernel_bridge import demo
        r = demo(); assert "simulation" in r; assert "resolutions" in r

class TestPipelineEngine:
    def test_create_and_run(self):
        from lab.pipeline_engine import PipelineEngine
        e = PipelineEngine(42); g = e.create_graph("test")
        g.add_step("a", lambda x: 1); g.add_step("b", lambda x: 2)
        g.connect("a", "b"); r = e.run("test")
        assert r["steps_executed"] == 2
    def test_demo(self):
        from lab.pipeline_engine import demo
        r = demo(); assert r["pipeline"]["steps_executed"] == 4

class TestCausalLoopDetector:
    def test_demo(self):
        from lab.experiments.causal_loop_detector import demo
        r = demo(); assert r["detector"] == "causal_loop_detector"; assert r["nodes"] > 0

class TestPhaseTransitionMonitor:
    def test_demo(self):
        from lab.experiments.phase_transition_monitor import demo
        r = demo(); assert r["readings"] == 20; assert r["transitions"] >= 0

class TestMemoryPalaceArchitect:
    def test_demo(self):
        from lab.experiments.memory_palace_architect import demo
        r = demo(); assert r["total_memories"] == 20; assert len(r["rooms"]) == 4

class TestSignalInterpreter:
    def test_demo(self):
        from lab.experiments.signal_interpreter import demo
        r = demo(); assert r["signals"] == 4; assert r["interpretations"] == 4

class TestRealityFabricWeaver:
    def test_demo(self):
        from lab.experiments.reality_fabric_weaver import demo
        r = demo(); assert r["threads"] == 5; assert r["weaves"] == 4

class TestTemporalEchoMap:
    def test_demo(self):
        from lab.experiments.temporal_echo_map import demo
        r = demo(); assert r["events"] == 15
