"""Wave 81 tests - Sandbox, Bridges, Streaming, and experimental modules."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


class TestSandboxEngine:
    def test_create_realm(self):
        from lab.sandbox_engine import SandboxEngine
        engine = SandboxEngine(seed=42)
        realm = engine.create_realm('test', 5, 5)
        assert realm.name == 'test'
        assert realm.width == 5

    def test_spawn_and_run(self):
        from lab.sandbox_engine import SandboxEngine
        engine = SandboxEngine(seed=42)
        engine.create_realm('void', 8, 8)
        engine.populate_realm('void', {'scout': 2, 'analyst': 1})
        result = engine.run_simulation('void', ticks=5)
        assert result['ticks'] == 5
        assert result['final_epoch'] == 5

    def test_agent_act(self):
        from lab.sandbox_engine import Agent
        agent = Agent('test_0', 'scout', seed=42)
        action = agent.act({})
        assert 'agent_id' in action
        assert agent.age == 1

    def test_demo(self):
        from lab.sandbox_engine import demo
        result = demo()
        assert 'engine_report' in result
        assert result['engine_report']['realm_count'] >= 2


class TestCrossSystemBridge:
    def test_register_and_send(self):
        from lab.cross_system_bridge import CrossSystemBridge
        bridge = CrossSystemBridge(seed=42)
        bridge.register_subsystem('a', ROOT / 'api')
        bridge.register_subsystem('b', ROOT / 'bridges')
        signal = bridge.send_signal('a', 'b', 'test', {'data': 1})
        assert signal.delivered is True

    def test_broadcast(self):
        from lab.cross_system_bridge import CrossSystemBridge
        bridge = CrossSystemBridge(seed=42)
        bridge.register_subsystem('a', ROOT / 'api')
        bridge.register_subsystem('b', ROOT / 'bridges')
        signals = bridge.broadcast('a', 'ping', {})
        assert len(signals) == 1

    def test_synergies(self):
        from lab.cross_system_bridge import CrossSystemBridge
        bridge = CrossSystemBridge(seed=42)
        bridge.register_subsystem('omega_prime', ROOT / 'omega_prime')
        bridge.register_subsystem('omega_fractal_engine', ROOT / 'omega_fractal_engine')
        synergies = bridge.discover_cross_module_synergies()
        assert isinstance(synergies, list)

    def test_demo(self):
        from lab.cross_system_bridge import demo
        result = demo()
        assert result['signal_count'] >= 0
        assert 'synergies' in result


class TestStreamingReactor:
    def test_publish_and_subscribe(self):
        from lab.streaming_reactor import StreamingReactor
        reactor = StreamingReactor()
        received = []
        reactor.subscribe('test', ['error'], lambda e: received.append(e))
        reactor.publish('error', 'test', {'msg': 'fail'})
        assert len(received) == 1

    def test_replay(self):
        from lab.streaming_reactor import StreamingReactor
        reactor = StreamingReactor()
        reactor.publish('a', 'src', {})
        reactor.publish('b', 'src', {})
        events = reactor.replay()
        assert len(events) == 2

    def test_stats(self):
        from lab.streaming_reactor import StreamingReactor
        reactor = StreamingReactor()
        for i in range(5):
            reactor.publish(f'type_{i % 2}', 'src', {})
        stats = reactor.stats()
        assert stats['total_published'] == 5

    def test_demo(self):
        from lab.streaming_reactor import demo
        result = demo()
        assert result['reactor'] == 'streaming_reactor'
        assert 'stats' in result


class TestAgentEcology:
    def test_demo(self):
        from lab.experiments.agent_ecology import demo
        result = demo()
        assert result['ecology'] == 'agent_ecology'
        assert len(result['species']) == 4
        assert result['ticks'] == 20


class TestDreamCatcher:
    def test_demo(self):
        from lab.experiments.dream_catcher import demo
        result = demo()
        assert result['dream_catcher'] == 'dream_catcher'
        assert result['analysis']['dream_count'] == 15


class TestChronicleWeaver:
    def test_demo(self):
        from lab.experiments.chronicle_weaver import demo
        result = demo()
        assert result['chronicle'] == 'chronicle_weaver'
        assert result['chapter_count'] >= 1


class TestTopologyMapper:
    def test_demo(self):
        from lab.experiments.topology_mapper import demo
        result = demo()
        assert result['topology'] == 'topology_mapper'
        assert result['nodes'] > 0


class TestAttentionField:
    def test_demo(self):
        from lab.experiments.attention_field import demo
        result = demo()
        assert result['attention_field'] == 'attention_field'
        assert result['well_count'] > 0


class TestParadoxResonator:
    def test_demo(self):
        from lab.experiments.paradox_resonator import demo
        result = demo()
        assert result['resonator'] == 'paradox_resonator'
        assert result['module_count'] > 0
