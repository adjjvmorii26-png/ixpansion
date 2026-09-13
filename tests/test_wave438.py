"""Tests for Wave 438 — Semantic Loom."""
import pytest
from api.wave438_semantic_loom import (
    SemanticThread, SemanticBridge, SemanticLoom, handler, coherence_vitals
)

def test_coherence_vitals():
    v = coherence_vitals()
    assert v["organ"] == "wave438_semantic_loom"
    assert v["wave"] == 438

def test_semantic_thread_init():
    t = SemanticThread("entropy", "disorder")
    assert t.concept == "entropy"
    assert t.thread_word == "disorder"
    assert 0 <= t.weight <= 1

def test_thread_resonate_different():
    a = SemanticThread("entropy", "disorder")
    b = SemanticThread("consciousness", "awareness")
    r = a.resonate(b)
    assert 0 <= r <= 1

def test_thread_resonate_same():
    a = SemanticThread("entropy", "disorder")
    b = SemanticThread("entropy", "randomness")
    r = a.resonate(b)
    assert r == 0.0

def test_semantic_bridge():
    bridge = SemanticBridge("a", "b", [{"resonance": 0.8}, {"resonance": 0.6}])
    assert bridge.strength == 0.7
    assert bridge.novelty >= 0

def test_semantic_loom_init():
    loom = SemanticLoom()
    assert loom.bridge_count == 0

def test_loom_extract_threads():
    loom = SemanticLoom()
    threads = loom.extract_threads("entropy")
    assert len(threads) == 7
    assert all(t.concept == "entropy" for t in threads)

def test_loom_weave():
    loom = SemanticLoom()
    bridge = loom.weave("entropy", "dream")
    assert bridge.concept_a == "entropy"
    assert bridge.concept_b == "dream"
    assert loom.bridge_count == 1

def test_loom_discover():
    loom = SemanticLoom()
    bridge = loom.discover_hidden_bridge(["entropy", "fire", "void", "music"])
    assert bridge is not None
    assert "strength" in bridge

def test_handler_status():
    result = handler({"action": "status"})
    assert result["action"] == "status"
    assert result["wave"] == 438

def test_handler_weave():
    result = handler({"action": "weave", "concept_a": "entropy", "concept_b": "dream"})
    assert result["action"] == "weave"
    assert "bridge" in result

def test_handler_discover():
    result = handler({"action": "discover", "concepts": ["entropy", "void", "fire"]})
    assert result["action"] == "discover"

def test_handler_threads():
    result = handler({"action": "threads", "concept": "entropy"})
    assert result["action"] == "threads"
    assert len(result["threads"]) == 7

def test_handler_unknown():
    result = handler({"action": "unknown"})
    assert "error" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
