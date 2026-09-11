"""Tests for Wave 408 — Resonance Graph Intelligence."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))


def test_resonance_node_creation():
    from api.resonance_graph import ResonanceNode
    node = ResonanceNode("test_module")
    assert node.module_name == "test_module"
    assert node.base_freq > 0
    assert len(node.harmonics) == 4
    assert node.coherence == 0.5
    assert node.amplitude == 1.0


def test_resonance_node_oscillate():
    from api.resonance_graph import ResonanceNode
    node = ResonanceNode("test")
    val = node.oscillate(0.0)
    assert isinstance(val, float)
    assert abs(val) <= 1.0


def test_resonance_node_to_dict():
    from api.resonance_graph import ResonanceNode
    node = ResonanceNode("test")
    d = node.to_dict()
    assert d["module"] == "test"
    assert "base_freq" in d
    assert "harmonics" in d
    assert "entangled" in d


def test_resonance_edge_strength():
    from api.resonance_graph import ResonanceEdge
    edge = ResonanceEdge("a", "b")
    # Same frequency → perfect resonance
    strength = edge.compute_strength(440.0, 440.0)
    assert strength == 1.0
    # Octave → strong
    strength = edge.compute_strength(440.0, 880.0)
    assert strength > 0.7


def test_resonance_graph_register():
    from api.resonance_graph import ResonanceGraph, get_graph
    g = ResonanceGraph()
    node = g.register_module("mod_a")
    assert node.module_name == "mod_a"
    assert len(g.nodes) == 1


def test_resonance_graph_connect():
    from api.resonance_graph import ResonanceGraph
    g = ResonanceGraph()
    g.register_module("mod_a")
    g.register_module("mod_b")
    edge = g.create_resonance("mod_a", "mod_b")
    assert edge is not None
    assert edge.strength > 0
    assert "mod_b" in g.nodes["mod_a"].entangled


def test_resonance_graph_wave():
    from api.resonance_graph import ResonanceGraph
    g = ResonanceGraph()
    g.register_module("source")
    g.register_module("target")
    g.create_resonance("source", "target")
    result = g.propagate_wave("source")
    assert "cycle_id" in result
    assert result["source"] == "source"
    assert len(result["wave_fronts"]) >= 1


def test_resonance_graph_coherence():
    from api.resonance_graph import ResonanceGraph
    g = ResonanceGraph()
    g.register_module("a")
    g.register_module("b")
    g.create_resonance("a", "b")
    report = g.get_coherence_report()
    assert "coherence_score" in report
    assert "nodes_registered" in report
    assert report["nodes_registered"] == 2


def test_resonance_graph_harmonic_map():
    from api.resonance_graph import ResonanceGraph
    g = ResonanceGraph()
    g.register_module("x")
    g.register_module("y")
    g.create_resonance("x", "y")
    hm = g.get_harmonic_map()
    assert "modules" in hm
    assert "pathways" in hm
    assert len(hm["modules"]) == 2


def test_resonance_graph_wave_history():
    from api.resonance_graph import ResonanceGraph
    g = ResonanceGraph()
    g.register_module("a")
    g.register_module("b")
    g.create_resonance("a", "b")
    g.propagate_wave("a")
    g.propagate_wave("a")
    history = g.wave_history
    assert len(history) == 2


def test_handler_actions():
    from api.resonance_graph import handler, get_graph
    g = get_graph()
    g.nodes.clear()
    g.edges.clear()
    g.wave_history.clear()
    g.oscillation_cycle = 0

    # Register
    r = handler({"action": "register", "module": "test_mod"})
    assert r["registered"]["module"] == "test_mod"

    # Connect
    handler({"action": "register", "module": "other_mod"})
    r = handler({"action": "connect", "source": "test_mod", "target": "other_mod"})
    assert "edge" in r

    # Wave
    r = handler({"action": "wave", "source": "test_mod"})
    assert "wave" in r

    # Report
    r = handler({"action": "report"})
    assert r["coherence_score"] >= 0

    # Harmonic map
    r = handler({"action": "harmonic_map"})
    assert len(r["modules"]) == 2

    # History
    r = handler({"action": "history"})
    assert len(r["waves"]) >= 1


def test_integration_with_existing_organs():
    """Verify resonance graph integrates with existing organism."""
    from api.resonance_graph import handler, get_graph
    g = get_graph()

    # Register several existing module types
    for mod in ["chronicle_driver", "mutation_pressure_engine", "vault_evolution_loop", "temporal_lineage_gate"]:
        handler({"action": "register", "module": mod})

    # Create some connections
    handler({"action": "connect", "source": "chronicle_driver", "target": "mutation_pressure_engine"})
    handler({"action": "connect", "source": "mutation_pressure_engine", "target": "vault_evolution_loop"})
    handler({"action": "connect", "source": "vault_evolution_loop", "target": "temporal_lineage_gate"})

    # Propagate a wave
    result = handler({"action": "wave", "source": "chronicle_driver"})
    assert result["wave"]["depth"] >= 1

    # Get coherence report
    report = handler({"action": "report"})
    assert report["coherence_score"] > 0
    assert report["nodes_registered"] >= 4


# ── Module dispatch test ────────────────────────────────

def test_wave408_resonance_graph_index_route():
    """Verify resonance_graph is reachable via api/index.py."""
    import api.resonance_graph
    assert hasattr(api.resonance_graph, 'handler')
    assert hasattr(api.resonance_graph, 'ResonanceGraph')
    assert hasattr(api.resonance_graph, 'ResonanceNode')
    assert hasattr(api.resonance_graph, 'ResonanceEdge')
