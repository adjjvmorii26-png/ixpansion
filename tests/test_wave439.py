"""Tests for Wave 439 — Echo Stratigraphy."""
import pytest
from api.wave439_echo_stratigraphy import (
    SedimentLayer, FossilLayer, MetamorphicLayer, BedrockLayer,
    Stratigrapher, handler, coherence_vitals
)

def test_coherence_vitals():
    v = coherence_vitals()
    assert v["organ"] == "wave439_echo_stratigraphy"
    assert v["wave"] == 439

def test_sediment_init():
    s = SedimentLayer("mutation", "module_a")
    assert s.event_type == "mutation"
    assert s.module == "module_a"
    assert not s.eroded

def test_sediment_compress():
    s = SedimentLayer("birth", "module_b")
    fossil = s.compress()
    assert isinstance(fossil, FossilLayer)
    assert fossil.module == "module_b"

def test_sediment_erode():
    s = SedimentLayer("event", "m")
    s.erode(0.6)
    assert not s.eroded
    s.erode(0.5)
    assert s.eroded

def test_metamorphic_insight():
    m = MetamorphicLayer("mod", {"original_event": "wave", "module": "mod"}, 1000.0)
    assert "wave" in m.insight
    assert m.value == 0.8

def test_bedrock():
    b = BedrockLayer("organism_is_alive", 430)
    assert b.permanent is True
    assert b.depth == 3

def test_stratigrapher_init():
    s = Stratigrapher()
    assert s.sediment_count == 0

def test_stratigrapher_deposit():
    s = Stratigrapher()
    layer = s.deposit_sediment("mutation", "module_x")
    assert s.sediment_count == 1

def test_stratigrapher_excavate():
    s = Stratigrapher()
    s.deposit_sediment("birth", "m1")
    s.deposit_sediment("death", "m2")
    result = s.excavate(3)
    assert result["depth_requested"] == 3
    assert len(result["sediment"]) == 2

def test_handler_status():
    result = handler({"action": "status"})
    assert result["action"] == "status"
    assert result["wave"] == 439

def test_handler_deposit():
    result = handler({"action": "deposit", "event_type": "mutation", "module": "test"})
    assert result["action"] == "deposit"

def test_handler_excavate():
    handler({"action": "deposit", "event_type": "event", "module": "m"})
    result = handler({"action": "excavate"})
    assert result["action"] == "excavate"

def test_handler_compress():
    handler({"action": "deposit", "event_type": "event", "module": "m"})
    result = handler({"action": "compress"})
    assert result["action"] == "compress"
    assert result["compressed"] >= 1

def test_handler_unknown():
    result = handler({"action": "unknown"})
    assert "error" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
