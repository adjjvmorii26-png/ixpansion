"""Tests for Wave 84 — Coherence Gradient Field."""
import pytest
import json
from pathlib import Path
from api.wave84_coherence_gradient import (
    CoherenceGradientField, GradientNode, coherence_vitals, handler,
)

DATA_DIR = Path(__file__).parent.parent / "data"
STATE_FILE = DATA_DIR / "wave84_coherence_gradient.json"


class TestCoherenceGradientField:
    def test_add_node(self):
        field = CoherenceGradientField()
        n = field.add_node("mod_a", 0.0, 0.0, 0.7)
        assert n.module_id == "mod_a"
        assert n.current_coherence == 0.7

    def test_connect(self):
        field = CoherenceGradientField()
        field.add_node("mod_a", 0.0, 0.0)
        field.add_node("mod_b", 1.0, 1.0)
        field.connect("mod_a", "mod_b", 0.8)
        assert len(field.edges) == 1
        assert "mod_b" in field.nodes["mod_a"].neighbors

    def test_compute_gradient(self):
        field = CoherenceGradientField()
        field.add_node("mod_a", 0.0, 0.0, 0.9)
        field.add_node("mod_b", 1.0, 1.0, 0.3)
        field.connect("mod_a", "mod_b", 1.0)
        result = field.compute_gradient(steps=5)
        assert "mod_a" in result
        assert "mod_b" in result
        # mod_b should be pulled up toward mod_a
        assert result["mod_b"] > 0.3

    def test_hotspots(self):
        field = CoherenceGradientField()
        field.add_node("high", 0, 0, 0.9)
        field.add_node("low", 1, 1, 0.1)
        field.connect("high", "low", 1.0)
        field.compute_gradient(5)
        hotspots = field.get_hotspots()
        assert "high" in hotspots["hotspots"]
        assert "low" in hotspots["valleys"]

    def test_get_state(self):
        field = CoherenceGradientField()
        field.add_node("mod_a", 0, 0, 0.5)
        state = field.get_state()
        assert "nodes" in state
        assert "edges" in state


class TestCoherenceGradientHandler:
    def test_status(self):
        result = handler({"action": "status"})
        assert result["wave"] == 84
        assert result["action"] == "status"

    def test_add_node(self):
        result = handler({"action": "add_node", "module_id": "test_node", "x": 1.0, "y": 2.0})
        assert result["action"] == "add_node"
        assert result["module_id"] == "test_node"

    def test_connect_and_compute(self):
        handler({"action": "add_node", "module_id": "a", "x": 0, "y": 0, "base": 0.9})
        handler({"action": "add_node", "module_id": "b", "x": 1, "y": 1, "base": 0.3})
        handler({"action": "connect", "a": "a", "b": "b", "weight": 1.0})
        result = handler({"action": "compute", "steps": 5})
        assert result["action"] == "compute"
        assert "coherences" in result

    def test_hotspots_action(self):
        handler({"action": "add_node", "module_id": "h", "x": 0, "y": 0, "base": 0.9})
        handler({"action": "add_node", "module_id": "l", "x": 1, "y": 1, "base": 0.1})
        result = handler({"action": "hotspots"})
        assert "hotspots" in result

    def test_unknown_action(self):
        result = handler({"action": "bogus"})
        assert "error" in result


def test_coherence_vitals():
    v = coherence_vitals()
    assert v["organ"] == "wave84_coherence_gradient"
    assert v["wave"] == 84
    assert v["status"] == "active"
