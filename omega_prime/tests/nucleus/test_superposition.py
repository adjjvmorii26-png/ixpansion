import pytest
from omega_prime.nucleus.kernel.superposition import SuperpositionState


class TestSuperposition:
    def test_single_branch_collapses_immediately(self):
        sup = SuperpositionState()
        sup.add_branch({"intent": "move"}, 1.0)
        result = sup.collapse(rng_seed=42)
        assert result == {"intent": "move"}

    def test_multi_branch_deterministic_with_seed(self):
        sup = SuperpositionState()
        sup.add_branch({"intent": "a"}, 0.9)
        sup.add_branch({"intent": "b"}, 0.1)
        r1 = sup.collapse(rng_seed=7)
        sup.reset()
        sup.add_branch({"intent": "a"}, 0.9)
        sup.add_branch({"intent": "b"}, 0.1)
        r2 = sup.collapse(rng_seed=7)
        assert r1 == r2

    def test_invalid_amplitude_raises(self):
        sup = SuperpositionState()
        with pytest.raises(ValueError):
            sup.add_branch({}, 0.0)

    def test_probabilities_sum_to_one(self):
        sup = SuperpositionState()
        sup.add_branch({"intent": "x"}, 0.5)
        sup.add_branch({"intent": "y"}, 0.5)
        probs = sup.probabilities()
        total = sum(p["p"] for p in probs)
        assert total == pytest.approx(1.0, abs=0.01)

    def test_is_superposed(self):
        sup = SuperpositionState()
        assert not sup.is_superposed
        sup.add_branch({"a": 1}, 0.5)
        sup.add_branch({"b": 2}, 0.5)
        assert sup.is_superposed
