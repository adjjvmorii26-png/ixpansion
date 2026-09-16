"""Tests for Wave 751 — Evolution Kernel."""
import pytest

def _import_wave(module_name):
    import importlib
    return importlib.import_module(f"api.{module_name}")

class TestWave751EvolutionKernel:
    def test_module_import(self):
        m = _import_wave("wave751_evolution_kernel")
        assert m.NAME == "evolution_kernel"
        assert m.WAVE == 751

    def test_observe(self):
        m = _import_wave("wave751_evolution_kernel")
        r = m.handler({"action": "observe", "modules": ["coherence_bridge", "dream_compiler", "skill_builder"], "signals": {"instability": 0.8}})
        assert r["wave"] == 751
        assert len(r["proposals"]) >= 1
        assert "entropy" in r

    def test_decide(self):
        m = _import_wave("wave751_evolution_kernel")
        r = m.handler({"action": "observe", "modules": ["a_module"], "signals": {}})
        pid = r["proposals"][0]["id"]
        d = m.handler({"action": "decide", "proposal_id": pid, "decision": "adopt"})
        assert d["decision"]["decision"] == "adopt"

    def test_lineage(self):
        m = _import_wave("wave751_evolution_kernel")
        r = m.handler({"action": "lineage", "wave": 730, "wave_end": 751})
        assert r["span"] == 22

    def test_coherence_vitals(self):
        m = _import_wave("wave751_evolution_kernel")
        v = m.coherence_vitals()
        assert v["wave"] == 751
        assert v["status"] == "active"

    def test_resonates_with(self):
        m = _import_wave("wave751_evolution_kernel")
        r = m.resonates_with()
        assert 734 in r

if __name__ == "__main__":
    pytest.main([__file__, "-q"])
