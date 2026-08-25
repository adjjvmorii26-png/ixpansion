from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

class TestAgentSpeciesBridge:
    def test_spawn_and_simulate(self):
        from lab.agent_species_bridge import SpeciesBridge
        b = SpeciesBridge(42)
        b.spawn("sentinel", 2); b.spawn("architect", 2); b.spawn("wanderer", 2)
        result = b.simulate(ticks=5, environment={"threat_level": 7})
        assert result["ticks"] == 5
    def test_deliberation(self):
        from lab.agent_species_bridge import AgentSpecies
        a = AgentSpecies("test", "sentinel", 42)
        a.perceive({"threat_level": 8})
        d = a.deliberate()
        assert d["intent"] == "alert"
    def test_demo(self):
        from lab.agent_species_bridge import demo
        r = demo(); assert r["bridge_report"]["total_agents"] >= 3

class TestHexDialectBridge:
    def test_translate(self):
        from lab.hex_dialect_bridge import DialectBridge
        b = DialectBridge()
        r = b.translate({"a": 1}, "alpha", "delta")
        assert "body" in r
    def test_broadcast(self):
        from lab.hex_dialect_bridge import DialectBridge
        b = DialectBridge()
        r = b.broadcast({"x": 1}, "alpha")
        assert len(r) == 2
    def test_demo(self):
        from lab.hex_dialect_bridge import demo
        r = demo(); assert r["translation_count"] >= 3

class TestCognitionEngine:
    def test_process(self):
        from lab.cognition_engine import CognitionEngine
        e = CognitionEngine(42)
        r = e.process([{"a": 1}], ["p1", "p2"])
        assert "dream" in r
    def test_demo(self):
        from lab.cognition_engine import demo
        r = demo(); assert "cognition" in r

class TestMessagingBridge:
    def test_emit_and_subscribe(self):
        from lab.messaging_bridge import MessagingBridge
        b = MessagingBridge(42); received = []
        b.on("test", lambda m: received.append(m))
        b.emit("test", {"x": 1}); assert len(received) == 1
    def test_channels(self):
        from lab.messaging_bridge import MessagingBridge
        b = MessagingBridge(42); b.create_channel("ch1")
        b.send_to_channel("ch1", {"data": 1})
        assert len(b.channels["ch1"].buffer) == 1
    def test_demo(self):
        from lab.messaging_bridge import demo
        r = demo(); assert r["total_messages"] >= 2

class TestSwarmIntelligence:
    def test_demo(self):
        from lab.experiments.swarm_intelligence import demo
        r = demo(); assert r["agents"] == 20; assert r["epoch"] == 30

class TestSignalPropagation:
    def test_demo(self):
        from lab.experiments.signal_propagation import demo
        r = demo(); assert r["propagator"] == "signal_propagation"

class TestKnowledgeCrystallizer:
    def test_demo(self):
        from lab.experiments.knowledge_crystallizer import demo
        r = demo(); assert r["patterns"]["total"] > 0

class TestEmergenceDetector:
    def test_demo(self):
        from lab.experiments.emergence_detector import demo
        r = demo(); assert r["behaviors"] == 30

class TestGenomeSequencer:
    def test_demo(self):
        from lab.experiments.genome_sequencer import demo
        r = demo(); assert r["generations"] > 0; assert r["best"]["fitness"] > 0

class TestEntanglementGraph:
    def test_demo(self):
        from lab.experiments.entanglement_graph import demo
        r = demo(); assert r["nodes"] > 0; assert r["entanglements"] >= 0
