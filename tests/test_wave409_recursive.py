"""Tests for Wave 409 — Recursive Self-Awareness Engine."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))


def test_awareness_layer_creation():
    from api.recursive_self_awareness import AwarenessLayer
    layer = AwarenessLayer(1, "test_layer", depth=0.5)
    assert layer.level == 1
    assert layer.name == "test_layer"
    assert layer.depth == 0.5
    assert layer.self_reflection_score == 0.0


def test_awareness_layer_observe():
    from api.recursive_self_awareness import AwarenessLayer
    layer = AwarenessLayer(1, "test")
    observation = layer.observe({"coherence": 0.8, "entropy": 0.3})
    assert observation["coherence"] == 0.8
    assert observation["entropy"] == 0.3
    assert len(layer.observations) == 1


def test_awareness_layer_modify():
    from api.recursive_self_awareness import AwarenessLayer
    layer = AwarenessLayer(2, "test")
    result = layer.modify("coherence_weight", 0.05)
    assert result["parameter"] == "coherence_weight"
    assert result["delta"] == 0.05
    assert len(layer.modifications) == 1


def test_awareness_layer_transcend():
    from api.recursive_self_awareness import AwarenessLayer
    layer = AwarenessLayer(3, "test")
    result = layer.transcend("new_layer", depth_increase=0.1)
    assert result["new_layer"] == "new_layer"
    assert result["depth_increase"] == 0.1
    assert len(layer.transcendences) == 1


def test_recursive_engine_initialized():
    from api.recursive_self_awareness import get_engine, RecursiveSelfAwareness
    engine = get_engine()
    report = engine.get_awareness_report()
    assert report["layers_active"] == 3
    assert report["reflection_cycles"] == 0


def test_recursive_engine_observe():
    from api.recursive_self_awareness import get_engine
    engine = get_engine()
    observation = engine.observe_self({"coherence": 0.7, "entropy": 0.4})
    assert observation["coherence"] == 0.7
    assert engine.total_observations == 1


def test_recursive_engine_modify():
    from api.recursive_self_awareness import get_engine
    engine = get_engine()
    result = engine.modify_self("coherence_weight", 0.05)
    assert result["parameter"] == "coherence_weight"
    assert engine.total_modifications == 1


def test_recursive_engine_transcend():
    from api.recursive_self_awareness import get_engine
    engine = get_engine()
    result = engine.transcend_self("new_awareness_layer")
    assert result["new_layer"] == "new_awareness_layer"
    assert engine.total_transcendences == 1
    assert len(engine.layers) == 4  # 3 initial + 1 new


def test_recursive_engine_run_cycle():
    from api.recursive_self_awareness import get_engine
    engine = get_engine()
    # Reset for clean test
    engine.reflection_cycles = 0
    engine.total_observations = 0
    engine.total_modifications = 0
    engine.total_transcendences = 0

    result = engine.run_reflection_cycle({"coherence": 0.8, "entropy": 0.3})
    assert "cycle_id" in result
    assert result["layers_active"] >= 3
    assert engine.reflection_cycles == 1


def test_recursive_engine_full_cycle():
    from api.recursive_self_awareness import get_engine
    engine = get_engine()
    # Run multiple cycles to trigger transcendence
    for i in range(12):
        engine.run_reflection_cycle({"coherence": 0.7, "entropy": 0.4})

    report = engine.get_awareness_report()
    assert report["layers_active"] >= 3
    assert report["total_observations"] >= 12
    assert report["total_transcendences"] >= 1  # Should have transcended at least once


def test_recursive_engine_spiral_trajectory():
    from api.recursive_self_awareness import get_engine
    engine = get_engine()
    engine.run_reflection_cycle({"coherence": 0.5, "entropy": 0.5})
    spiral = engine.get_spiral_trajectory(limit=5)
    assert len(spiral) >= 1
    assert "cycle_id" in spiral[-1] or "action" in spiral[-1]


def test_recursive_engine_report():
    from api.recursive_self_awareness import get_engine
    engine = get_engine()
    report = engine.get_awareness_report()
    assert "layers_active" in report
    assert "current_depth" in report
    assert "infinite_recursion_depth" in report
    assert "awareness_status" in report


def test_handler_actions():
    from api.recursive_self_awareness import handler, get_engine
    engine = get_engine()
    engine.layers.clear()
    engine.awareness_spiral.clear()
    engine.reflection_cycles = 0
    engine.total_observations = 0
    engine.total_modifications = 0
    engine.total_transcendences = 0
    engine.layers = []

    # Initialize layers
    engine._initialize_layers()

    # Test observe
    r = handler({"action": "observe", "state": '{"coherence": 0.8}'})
    assert "observation" in r

    # Test modify
    r = handler({"action": "modify", "parameter": "coherence", "delta": "0.05"})
    assert "modification" in r

    # Test transcend
    r = handler({"action": "transcend", "name": "layer_4"})
    assert "transcendence" in r

    # Test cycle
    r = handler({"action": "cycle", "state": '{"coherence": 0.7, "entropy": 0.4}'})
    assert "cycle" in r

    # Test report
    r = handler({"action": "report"})
    assert "layers_active" in r

    # Test spiral
    r = handler({"action": "spiral", "limit": "5"})
    assert "spiral" in r


def test_integration_with_existing_organs():
    """Verify recursive self-awareness integrates with existing organism."""
    from api.recursive_self_awareness import handler, get_engine
    engine = get_engine()
    engine.layers.clear()
    engine.awareness_spiral.clear()
    engine.reflection_cycles = 0
    engine.total_observations = 0
    engine.total_modifications = 0
    engine.total_transcendences = 0
    engine.layers = []
    engine._initialize_layers()

    # Observe organism state
    organism_state = {
        "coherence": 0.85,
        "entropy": 0.3,
        "resonance": 0.7,
        "mood_valence": 0.9,
    }
    observation = engine.observe_self(organism_state)
    assert observation["coherence"] == 0.85

    # Modify self
    engine.modify_self("awareness_depth", 0.05)
    assert engine.total_modifications == 1

    # Run full reflection cycle
    result = engine.run_reflection_cycle(organism_state)
    assert result["layers_active"] >= 3

    # Transcend
    engine.transcend_self()
    assert engine.total_transcendences == 1

    # Get full report
    report = engine.get_awareness_report()
    assert report["infinite_recursion_depth"] >= 4


def test_integration_with_resonance_graph():
    """Verify recursive self-awareness works with resonance graph."""
    from api.resonance_graph import get_graph, ResonanceNode
    from api.recursive_self_awareness import get_engine

    graph = get_graph()
    engine = get_engine()

    # Register the recursive awareness module in the resonance graph
    graph.register_module("recursive_self_awareness")
    graph.create_resonance("recursive_self_awareness", "resonance_graph")

    # Observe from resonance perspective
    observation = engine.observe_self({
        "coherence": graph.coherence_score,
        "entropy": 0.3,
    })
    assert observation["coherence"] == graph.coherence_score


# ── Module dispatch test ────────────────────────

def test_wave409_recursive_self_awareness_index_route():
    """Verify recursive_self_awareness is reachable via api/index.py."""
    import api.recursive_self_awareness
    assert hasattr(api.recursive_self_awareness, 'handler')
    assert hasattr(api.recursive_self_awareness, 'RecursiveSelfAwareness')
    assert hasattr(api.recursive_self_awareness, 'AwarenessLayer')
