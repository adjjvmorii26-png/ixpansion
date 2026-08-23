import pytest
from omega_prime.nucleus.kernel.causal_graph import CausalGraph


class TestCausalGraph:
    def test_record_and_trace(self):
        graph = CausalGraph()
        root = graph.record_action("agent_a", "move", tick=1)
        mid = graph.record_action("agent_b", "alert", tick=2, causes=[root])
        leaf = graph.record_action("agent_c", "attack", tick=3, causes=[mid])

        ancestors = graph.trace_root_causes(leaf)
        assert len(ancestors) >= 2
        assert ancestors[0].tick <= ancestors[-1].tick

    def test_anomaly_flagging(self):
        graph = CausalGraph()
        nid = graph.record_action("x", "scan", tick=1)
        graph.record_effect(nid, "unexpected_explosion", is_anomaly=True)
        anomalies = graph.find_anomaly_sources()
        assert len(anomalies) == 1
        assert anomalies[0].is_anomaly

    def test_stats(self):
        graph = CausalGraph()
        n1 = graph.record_action("a", "move", 1)
        n2 = graph.record_action("b", "move", 2, causes=[n1])
        stats = graph.stats
        assert stats["nodes"] == 2
        assert stats["edges"] == 1

    def test_trace_depth_limit(self):
        graph = CausalGraph(max_depth=2)
        n1 = graph.record_action("a", "act", 1)
        n2 = graph.record_action("b", "act", 2, causes=[n1])
        n3 = graph.record_action("c", "act", 3, causes=[n2])
        n4 = graph.record_action("d", "act", 4, causes=[n3])
        ancestors = graph.trace_root_causes(n4, max_depth=1)
        assert len(ancestors) <= 1
