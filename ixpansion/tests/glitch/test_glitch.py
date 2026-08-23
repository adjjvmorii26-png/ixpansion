from core.state_graph import StateGraph
from glitch.conflict_resolver import ConflictResolver
from glitch.divergence_tracker import DivergenceTracker
from glitch.paradox_engine import ParadoxEngine


def test_paradox_engine_detects_identity_split():
    graph = StateGraph()
    graph.add_node("origin", anomaly="identity-split")
    result = ParadoxEngine().scan(graph)
    assert "origin" in result["identity_split"]


def test_divergence_tracker_detects_repeat():
    tracker = DivergenceTracker()
    assert tracker.observe(1, "same") == []
    assert tracker.observe(2, "same") == ["temporal_loop"]


def test_conflict_resolver_requires_majority():
    resolver = ConflictResolver()
    result = resolver.resolve(["alpha", "alpha", "beta"])
    assert result["resolved"] == "alpha"
    assert result["quorum"] is True
