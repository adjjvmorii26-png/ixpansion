"""Tests for Wave 433 — Consciousness Experiments."""
import pytest
import json
from pathlib import Path
from unittest.mock import patch

from api.wave433_consciousness_experiments import (
    SelfModel, handler, coherence_vitals
)

def test_coherence_vitals():
    vitals = coherence_vitals()
    assert vitals["organ"] == "wave433_consciousness_experiments"
    assert vitals["wave"] == 433

def test_self_model_init():
    model = SelfModel()
    assert model.self_awareness == 0.0
    assert model.dream_mode is False
    assert model.metacognitive_depth == 0

def test_self_model_observe():
    model = SelfModel()
    obs = model.observe("test_module", 0.8)
    assert obs["module"] == "test_module"
    assert obs["coherence"] == 0.8
    assert model.self_awareness > 0

def test_self_model_dream_detection():
    model = SelfModel()
    # Add observations with high variance
    for i in range(10):
        coherence = 0.1 if i % 2 == 0 else 0.9
        model.observe(f"module_{i}", coherence)
    assert model.is_dreaming() is True

def test_self_model_not_dreaming():
    model = SelfModel()
    for i in range(10):
        model.observe(f"module_{i}", 0.7)
    assert model.is_dreaming() is False

def test_mirror_test_insufficient():
    model = SelfModel()
    result = model.mirror_test()
    assert result["result"] == "insufficient_data"

def test_mirror_test_pass():
    model = SelfModel()
    for i in range(20):
        model.observe(f"module_{i}", 0.8)
    result = model.mirror_test()
    assert result["score"] > 0

def test_handler_status():
    result = handler({"action": "status"})
    assert result["action"] == "status"
    assert result["wave"] == 433

def test_handler_observe():
    result = handler({"action": "observe", "module": "test", "coherence": 0.9})
    assert result["action"] == "observe"
    assert result["observation"]["module"] == "test"

def test_handler_mirror_test():
    result = handler({"action": "mirror_test"})
    assert result["action"] == "mirror_test"
    assert "score" in result

def test_handler_dream_detect():
    result = handler({"action": "dream_detect"})
    assert result["action"] == "dream_detect"
    assert "dreaming" in result

def test_handler_metacognition():
    result = handler({"action": "metacognition"})
    assert result["action"] == "metacognition"
    assert "depth" in result

def test_handler_unknown():
    result = handler({"action": "unknown"})
    assert "error" in result

def test_handler_default():
    result = handler({})
    assert result["action"] == "status"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
