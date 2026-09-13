"""Tests for Wave 441 — Wave Composition."""
import pytest
from api.wave441_wave_composition import WaveComposition, handler, coherence_vitals, WAVE_VOICES

def test_coherence_vitals():
    v = coherence_vitals()
    assert v["organ"] == "wave441_wave_composition"
    assert v["wave"] == 441

def test_wave_voices_complete():
    assert len(WAVE_VOICES) == 9

def test_composition_init():
    c = WaveComposition()
    assert c.harmonic_count == 0

def test_compose_subset():
    c = WaveComposition()
    result = c.compose(["vault", "weather"])
    assert "vault" in result["results"]
    assert "weather" in result["results"]
    assert result["avg_harmonic"] >= 0

def test_compose_all():
    c = WaveComposition()
    result = c.compose(list(WAVE_VOICES.keys()))
    assert len(result["results"]) == 9

def test_handler_status():
    result = handler({"action": "status"})
    assert result["action"] == "status"
    assert result["wave"] == 441

def test_handler_compose():
    result = handler({"action": "compose", "voices": ["vault", "weather"]})
    assert result["action"] == "compose"
    assert "composition" in result

def test_handler_compose_all():
    result = handler({"action": "compose_all"})
    assert result["action"] == "compose_all"

def test_handler_unknown():
    result = handler({"action": "unknown"})
    assert "error" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
