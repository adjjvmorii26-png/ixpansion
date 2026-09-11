"""Tests for Wave 407 — Dream Forge."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))


def test_dream_forge_default():
    from api.dream_forge import get_dream_forge
    forge = get_dream_forge()
    report = forge.get_dream_report()
    assert "total_dreams" in report
    assert "total_patterns" in report
    assert "ready_to_incubate" in report

def test_dream_forge_dream():
    from api.dream_forge import get_dream_forge
    forge = get_dream_forge()
    # Feed some patterns first
    for i in range(5):
        forge.ingest_chronicle([{
            "event_type": f"test_event_{i}",
            "timestamp": 1000.0 + i,
            "data": {"value": i * 10},
            "hash": f"hash_{i}"
        }])
    dream = forge.dream()
    assert "id" in dream
    assert dream["module_spec"]["name"].startswith("dream_")
    assert "coherence_score" in dream

def test_dream_forge_incubate():
    from api.dream_forge import get_dream_forge
    forge = get_dream_forge()
    # Feed enough patterns
    for i in range(10):
        forge.ingest_chronicle([{
            "event_type": f"event_{i}",
            "timestamp": 1000.0 + i,
            "data": {"value": i},
            "hash": f"h{i}"
        }])
    # Dream multiple times
    for _ in range(5):
        forge.dream()
    incubated = forge.incubate()
    if incubated:
        assert "dream_id" in incubated
        assert "module" in incubated
        assert "coherence" in incubated

def test_dream_forge_report():
    from api.dream_forge import get_dream_forge
    forge = get_dream_forge()
    forge.ingest_chronicle([{"event_type": "test", "timestamp": 1.0, "data": {}, "hash": "x"}])
    forge.dream()
    report = forge.get_dream_report()
    assert report["total_dreams"] >= 1
    assert report["total_patterns"] >= 1

def test_dream_forge_empty():
    from api.dream_forge import get_dream_forge
    forge = get_dream_forge()
    result = forge.dream()
    assert result.get("dream") is None or "reason" in result

def test_dream_forge_module_spec():
    from api.dream_forge import DreamForge
    forge = DreamForge()
    for i in range(10):
        forge.ingest_chronicle([{
            "event_type": f"evt_{i}",
            "timestamp": float(i),
            "data": {"k": i},
            "hash": f"h{i:04d}"
        }])
    dream = forge.dream()
    spec = dream["module_spec"]
    assert "name" in spec
    assert spec["type"] in ("sensor", "processor", "memorizer", "transmitter", "guardian", "weaver")
    assert "born_from_dream" in spec and spec["born_from_dream"] is True
    assert "complexity" in spec

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
