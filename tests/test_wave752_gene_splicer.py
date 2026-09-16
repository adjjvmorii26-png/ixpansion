"""Tests for Wave 752 — Gene Splicer (DNA x evolution kernel child organs)."""
import pytest

def _import_wave(module_name):
    import importlib
    return importlib.import_module(f"api.{module_name}")

class TestWave752GeneSplicer:
    def test_module_import(self):
        m = _import_wave("wave752_gene_splicer")
        assert m.NAME == "gene_splicer"
        assert m.WAVE == 752

    def test_splice(self):
        m = _import_wave("wave752_gene_splicer")
        r = m.handler({"action": "splice", "donor_a": "wave734_repo_dna", "donor_b": "wave751_evolution_kernel"})
        assert r["ok"] is True
        assert "child_dna" in r
        assert "donor_a" in r["child_dna"] and "donor_b" in r["child_dna"]

    def test_merge(self):
        m = _import_wave("wave752_gene_splicer")
        r = m.handler({"action": "merge", "donor_a": "wave734_repo_dna", "donor_b": "wave751_evolution_kernel"})
        assert r["ok"] is True
        assert r["merged"]["parentage"] == ["wave734_repo_dna", "wave751_evolution_kernel"]

    def test_split(self):
        m = _import_wave("wave752_gene_splicer")
        r = m.handler({"action": "split", "donor": "wave734_repo_dna"})
        assert r["ok"] is True
        assert isinstance(r["halves"], list) and len(r["halves"]) >= 1

    def test_coherence_vitals(self):
        m = _import_wave("wave752_gene_splicer")
        v = m.coherence_vitals()
        assert v["wave"] == 752
        assert v["status"] == "active"

    def test_resonates_with(self):
        m = _import_wave("wave752_gene_splicer")
        r = m.resonates_with()
        assert 734 in r
        assert 751 in r

if __name__ == "__main__":
    pytest.main([__file__, "-q"])
