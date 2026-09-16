"""Tests for Waves 721-724: Coherence Bridge, Interstice Engine, Dream Compiler, Symbiosis Ecology."""
import json
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _load_data(name):
    p = ROOT / "data" / name
    if p.exists():
        return json.loads(p.read_text())
    return {}

def _import_wave(module_name):
    import importlib
    return importlib.import_module(f"api.{module_name}")

class TestWave721CoherenceBridge:
    def test_module_import(self):
        m = _import_wave("wave721_coherence_bridge")
        assert m.NAME == "coherence_bridge"
        assert m.WAVE == 721

    def test_coherence_vitals(self):
        m = _import_wave("wave721_coherence_bridge")
        v = m.coherence_vitals()
        assert v["wave"] == 721
        assert v["status"] == "active"

    def test_handler_status(self):
        m = _import_wave("wave721_coherence_bridge")
        r = m.handler({"action": "status"})
        assert r["wave"] == 721
        assert "bridge_count" in r

    def test_handler_scan(self):
        m = _import_wave("wave721_coherence_bridge")
        r = m.handler({"action": "scan"})
        assert r["wave"] == 721
        assert "bridges_found" in r or "action" in r

    def test_resonates_with(self):
        m = _import_wave("wave721_coherence_bridge")
        r = m.resonates_with()
        assert isinstance(r, list)
        assert 720 in r

class TestWave722IntersticeBridge:
    def test_module_import(self):
        m = _import_wave("wave722_interstice_bridge")
        assert m.NAME == "interstice_bridge"
        assert m.WAVE == 722

    def test_handler_scan(self):
        m = _import_wave("wave722_interstice_bridge")
        r = m.handler({"action": "scan"})
        assert r["wave"] == 722

    def test_handler_proposals(self):
        m = _import_wave("wave722_interstice_bridge")
        m.handler({"action": "scan"})
        r = m.handler({"action": "proposals"})
        assert r["wave"] == 722
        assert "proposals" in r

    def test_coherence_vitals(self):
        m = _import_wave("wave722_interstice_bridge")
        v = m.coherence_vitals()
        assert v["wave"] == 722
        assert v["status"] == "active"

class TestWave723DreamCompiler:
    def test_module_import(self):
        m = _import_wave("wave723_dream_compiler")
        assert m.NAME == "dream_compiler"
        assert m.WAVE == 723

    def test_dream(self):
        m = _import_wave("wave723_dream_compiler")
        r = m.handler({"action": "dream", "prompt": "test dream"})
        assert r["wave"] == 723
        assert r["action"] == "dream"
        assert "dream" in r
        assert r["dream"]["id"]

    def test_compile(self):
        m = _import_wave("wave723_dream_compiler")
        dream = m.handler({"action": "dream", "prompt": "compile test"})
        r = m.handler({"action": "compile", "dream_id": dream["dream"]["id"]})
        assert r["action"] == "compile"
        assert r["compiled"]["status"] == "compiled"

    def test_coherence_vitals(self):
        m = _import_wave("wave723_dream_compiler")
        v = m.coherence_vitals()
        assert v["wave"] == 723
        assert "dreams" in v

class TestWave724SymbiosisEcology:
    def test_module_import(self):
        m = _import_wave("wave724_symbiosis_ecology")
        assert m.NAME == "symbiosis_ecology"
        assert m.WAVE == 724

    def test_spawn(self):
        m = _import_wave("wave724_symbiosis_ecology")
        r = m.handler({"action": "spawn", "type": "explorer"})
        assert r["wave"] == 724
        assert "agent" in r

    def test_interact(self):
        m = _import_wave("wave724_symbiosis_ecology")
        spawn1 = m.handler({"action": "spawn", "type": "a"})
        spawn2 = m.handler({"action": "spawn", "type": "b"})
        r = m.handler({"action": "interact", "agent1": spawn1["agent"]["id"], "agent2": spawn2["agent"]["id"]})
        assert r["wave"] == 724
        assert r["interaction"]["type"] in ["cooperate", "compete", "mutualism", "parasitism", "commensalism"]

    def test_evolve(self):
        m = _import_wave("wave724_symbiosis_ecology")
        m.handler({"action": "spawn", "type": "a"})
        r = m.handler({"action": "evolve"})
        assert r["wave"] == 724
        assert "generations" in r

    def test_coherence_vitals(self):
        m = _import_wave("wave724_symbiosis_ecology")
        v = m.coherence_vitals()
        assert v["wave"] == 724
        assert v["status"] == "active"

if __name__ == "__main__":
    pytest.main([__file__, "-q"])
