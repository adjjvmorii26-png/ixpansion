"""Tests for Wave 662 — Dream Compiler v2."""
import pytest
from api.wave662_dream_compiler import handler, coherence_vitals, resonates_with
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave662_dream_compiler.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert r["residues"] == 0
    def test_distill(self):
        r = handler({"action": "distill", "residue": "tide", "source": "moonlayer"})
        assert r["ok"] is True; assert r["motif"]["residue"] == "tide"
    def test_compile(self):
        handler({"action": "distill", "residue": "tide"})
        r = handler({"action": "compile", "name": "tide_organ", "actions": ["sense", "seal"]})
        assert r["ok"] is True; assert r["organ"]["name"] == "tide_organ"; assert r["organ"]["status"] == "compiled"
    def test_compile_empty(self):
        r = handler({"action": "compile"}); assert r["ok"] is False
    def test_manifest(self):
        handler({"action": "distill", "residue": "tide"})
        handler({"action": "compile", "name": "tide_organ"})
        r = handler({"action": "manifest"}); assert r["ok"] is True; assert len(r["organs"]) == 1
    def test_unknown(self):
        r = handler({"action": "foo"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 662
class TestResonates:
    def test_list(self):
        assert "wave663_resonance_ledger" in resonates_with()
