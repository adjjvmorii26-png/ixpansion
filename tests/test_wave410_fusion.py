"""Tests for Wave 410 Fusion-Evolution organ."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave410_fusion as wf

def test_fusion_modules_present():
    assert len(wf.FUSION_MODULES) == 9
    assert "paradox_echo" in wf.FUSION_MODULES
    assert "mycelial_governor" in wf.FUSION_MODULES

def test_status_endpoint():
    result = wf.handler({"action": "status"})
    assert result["wave"] == 410
    assert result["realm"] == "fusion_evolution"
    assert result["count"] == 9

def test_fuse_pass():
    result = wf.handler({"action": "fuse", "module_a": "metaphor_forge", "module_b": "liminal_field"})
    assert result["status"] == "fused"
    assert "fusion" in result
    assert result["fusion"]["module_a"] == "metaphor_forge"

def test_fuse_invalid_modules():
    result = wf.handler({"action": "fuse", "module_a": "nope", "module_b": "liminal_field"})
    assert "error" in result

def test_veil_scan():
    result = wf.handler({"action": "veil_scan"})
    assert "revealed" in result
    assert isinstance(result["revealed"], list)

def test_coherence_vitals():
    vitals = wf.coherence_vitals()
    assert vitals["status"] == "active"
    assert vitals["coherence"] > 0.5

def test_data_files_persist():
    data_dir = Path(__file__).parent.parent / "data"
    for name in wf.FUSION_MODULES:
        assert (data_dir / f"{name}.json").exists(), f"missing {name}.json"
