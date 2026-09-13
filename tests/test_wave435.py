"""Tests for Wave 435 — Resonance Cartography."""
import pytest
from api.wave435_resonance_cartography import (
    ResonanceSignature, AttractionField, Cartographer, handler, coherence_vitals
)

def test_coherence_vitals():
    v = coherence_vitals()
    assert v["organ"] == "wave435_resonance_cartography"
    assert v["wave"] == 435

def test_resonance_signature_init():
    sig = ResonanceSignature("module_a")
    assert sig.module_id == "module_a"
    assert 0 <= sig.frequency <= 1
    assert 0 <= sig.amplitude <= 1
    assert len(sig.harmonics) == 4

def test_resonance_drift():
    sig = ResonanceSignature("module_b")
    old_phase = sig.phase
    sig.drift_tick(0.1)
    assert sig.drift != 0

def test_harmonic_distance():
    sig_a = ResonanceSignature("module_x")
    sig_b = ResonanceSignature("module_x")
    dist = sig_a.harmonic_distance(sig_b)
    assert dist == 0.0
    sig_c = ResonanceSignature("module_y")
    dist2 = sig_a.harmonic_distance(sig_c)
    assert dist2 >= 0.0

def test_attraction_field():
    sig_a = ResonanceSignature("a")
    sig_b = ResonanceSignature("b")
    field = AttractionField(sig_a, sig_b)
    assert 0 <= field.attraction <= 1
    assert field.force_type in ["resonance_bond", "gravitational_pull", "weak_association", "entangled_reject", "dissonance_field"]

def test_cartographer_register():
    c = Cartographer()
    sig = c.register_module("mod_1")
    assert "mod_1" in c.signatures

def test_cartographer_map():
    c = Cartographer()
    c.register_module("a")
    c.register_module("b")
    c.register_module("c")
    atlas = c.map_topology()
    assert atlas["total_modules"] == 3
    assert atlas["total_fields"] == 3

def test_cartographer_clusters():
    c = Cartographer()
    c.register_module("a")
    c.register_module("b")
    for i in range(5):
        c.register_module(f"d{i}")
    atlas = c.map_topology()
    assert "clusters" in atlas

def test_cartographer_drift():
    c = Cartographer()
    c.register_module("x")
    c.register_module("y")
    before = c.signatures["x"].drift
    c.drift_all(0.1)
    assert c.signatures["x"].drift != before

def test_handler_status():
    result = handler({"action": "status"})
    assert result["action"] == "status"
    assert result["wave"] == 435

def test_handler_register():
    result = handler({"action": "register", "module_id": "test_mod"})
    assert result["action"] == "register"
    assert result["total"] >= 1

def test_handler_map():
    handler({"action": "register", "module_id": "a"})
    handler({"action": "register", "module_id": "b"})
    result = handler({"action": "map"})
    assert result["action"] == "map"
    assert "total_modules" in result

def test_handler_unknown():
    result = handler({"action": "unknown"})
    assert "error" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
