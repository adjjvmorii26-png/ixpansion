"""Tests for Wave 411 Resonance Topology organ."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave411_topology as wt

def test_topology_builds():
    topo = wt.build_topology()
    assert topo["wave"] == 411
    assert topo["graph_stats"]["node_count"] > 0
    assert topo["graph_stats"]["edge_count"] > 0

def test_topology_includes_fusion_modules():
    topo = wt.build_topology()
    assert "metaphor_forge" in topo["modules"]
    assert "paradox_echo" in topo["modules"]
    assert "continuity_weaver" in topo["modules"]

def test_evolution_cycle():
    result = wt.handler({"action": "cycle", "module_a": "metaphor_forge", "module_b": "veil_lifter"})
    assert result["wave"] == 411
    assert result["cycle"]["fusion_result"] == "fused"
    assert result["cycle"]["topology_nodes"] > 0

def test_handler_valid_actions():
    assert "edges" in wt.handler({"action": "topology"})
    assert "error" in wt.handler({"action": "bogus"})

def test_coherence_vitals():
    vitals = wt.coherence_vitals()
    assert vitals["status"] == "active"
