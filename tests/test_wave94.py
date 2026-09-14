"""Tests for Wave 94 — Dream Compiler."""
import pytest
from api.wave94_dream_compiler import (
    CompiledModule, DreamCompiler, coherence_vitals, handler,
)


SAMPLE_DREAM = {
    "reality_fluidity": 0.72,
    "gravity_modifier": 0.6,
    "emotional_resonance": "chaotic",
    "layers": ["surreal_gravity", "time_dilation", "reality_fluidity"],
}


class TestCompiledModule:
    def test_init(self):
        mod = CompiledModule("m1", "dream_test", "physics_layer", "abcd", "skel", 0.8)
        assert mod.module_id == "m1"
        assert mod.confidence == 0.8

    def test_confidence_clamped(self):
        mod = CompiledModule("m2", "d", "l", "ab", "s", 2.0)
        assert mod.confidence == 1.0

    def test_to_dict(self):
        mod = CompiledModule("m3", "d", "l", "ab", "skeleton body", 0.5)
        d = mod.to_dict()
        assert d["module_id"] == "m3"
        assert "skeleton_preview" in d
        assert "confidence" in d


class TestDreamCompiler:
    def test_compile_produces_modules(self):
        compiler = DreamCompiler()
        modules = compiler.compile(SAMPLE_DREAM)
        assert len(modules) == 3
        assert all(isinstance(m, CompiledModule) for m in modules)

    def test_compile_derives_from_physics(self):
        compiler = DreamCompiler()
        modules = compiler.compile({"reality_fluidity": 0.5, "gravity_modifier": 1.0})
        assert len(modules) >= 2

    def test_skeleton_is_python(self):
        compiler = DreamCompiler()
        modules = compiler.compile(SAMPLE_DREAM)
        skeleton = modules[0].skeleton
        assert "def handler(req: dict) -> dict:" in skeleton
        assert "def coherence_vitals() -> dict:" in skeleton

    def test_execute_compiled(self):
        compiler = DreamCompiler()
        modules = compiler.compile(SAMPLE_DREAM)
        out = compiler.execute(modules[0].module_id)
        assert out["ok"] is True
        assert out["execution_count"] == 1

    def test_execute_unknown(self):
        compiler = DreamCompiler()
        out = compiler.execute("nope")
        assert out["ok"] is False

    def test_vitals(self):
        compiler = DreamCompiler()
        vitals = compiler.coherence_vitals()
        assert vitals["wave"] == 94
        assert "compiled_modules" in vitals


class TestHandler:
    def test_status(self):
        out = handler({"action": "status"})
        assert out["action"] == "status"
        assert out["wave"] == 94

    def test_compile(self):
        out = handler({"action": "compile", "dream_state": SAMPLE_DREAM})
        assert out["count"] == 3

    def test_compile_json_string(self):
        import json
        out = handler({"action": "compile", "dream_state": json.dumps(SAMPLE_DREAM)})
        assert out["count"] == 3

    def test_list(self):
        out = handler({"action": "list"})
        assert out["action"] == "list"

    def test_unknown_action(self):
        out = handler({"action": "bogus"})
        assert out["ok"] is False

    def test_coherence_vitals(self):
        vitals = coherence_vitals()
        assert vitals["wave"] == 94
