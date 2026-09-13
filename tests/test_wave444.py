"""Tests for Wave 444 — Dream Synthesis."""
import pytest
from api.wave444_dream_synthesis import Dream, DreamSynthesizer, handler, coherence_vitals, DREAM_ARCHETYPES

def test_coherence_vitals():
    v = coherence_vitals()
    assert v["organ"] == "wave444_dream_synthesis"
    assert v["wave"] == 444

def test_dream_archetypes():
    assert len(DREAM_ARCHETYPES) == 10
    for arch, data in DREAM_ARCHETYPES.items():
        assert "tension" in data
        assert "resolution" in data

def test_dream_init():
    residues = {"weather": "storm", "paradox_count": 5}
    dream = Dream(residues)
    assert dream.dream_id
    assert dream.archetype in DREAM_ARCHETYPES
    assert dream.narrative
    assert len(dream.generated_artifacts) >= 2
    assert dream.emotional_tone

def test_dream_narrative():
    residues = {"weather": "storm"}
    dream = Dream(residues)
    arch = DREAM_ARCHETYPES[dream.archetype]
    assert arch["tension"].replace("_", " ") in dream.narrative
    assert arch["resolution"].replace("_", " ") in dream.narrative

def test_dream_artifacts():
    dream = Dream({})
    artifacts = dream.generated_artifacts
    assert 2 <= len(artifacts) <= 5
    for a in artifacts:
        assert "type" in a
        assert "potency" in a
        assert 0 <= a["potency"] <= 1

def test_synthesizer_init():
    s = DreamSynthesizer()
    assert s.dream_count == 0

def test_synthesize():
    s = DreamSynthesizer()
    activity = {"weather": "storm", "paradox_count": 5}
    dream = s.synthesize(activity)
    assert dream.archetype in DREAM_ARCHETYPES
    assert s.dream_count == 1

def test_dream_report():
    s = DreamSynthesizer()
    s.synthesize({})
    report = s.get_dream_report()
    assert report["total_dreams"] == 1
    assert "archetypes" in report
    assert "emotional_tones" in report

def test_handler_status():
    result = handler({"action": "status"})
    assert result["action"] == "status"
    assert result["wave"] == 444

def test_handler_dream():
    result = handler({"action": "dream"})
    assert result["action"] == "dream"
    assert "dream" in result

def test_handler_report():
    handler({"action": "dream"})
    result = handler({"action": "report"})
    assert result["action"] == "report"

def test_handler_unknown():
    result = handler({"action": "unknown"})
    assert "error" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
