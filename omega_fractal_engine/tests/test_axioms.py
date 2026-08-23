import pytest
from omega_fractal_engine.nucleus.kernel.axioms import enforce, enforce_all, AXIOMS


class TestAxioms:
    def test_all_axioms_exist(self):
        assert len(AXIOMS) >= 5

    def test_entropy_conservation_passes(self):
        assert enforce("A1", {"total_entropy": 10}) is True
        assert enforce("A1", {"total_entropy": 0}) is True

    def test_entropy_conservation_fails(self):
        assert enforce("A1", {"total_entropy": -5}) is False

    def test_enforce_all(self):
        results = enforce_all({
            "A1": {"total_entropy": 5},
            "A4": {"is_superposed": True, "is_measured": False},
        })
        assert results["A1"] is True
        assert results["A4"] is True

    def test_unknown_axiom_raises(self):
        with pytest.raises(KeyError):
            enforce("A999", {})
