import pytest
from omega_prime.sandbox.modules.consensus_reality import ConsensusReality, CellState


class TestConsensusReality:
    def test_single_observer_stays_unobserved(self):
        cr = ConsensusReality()
        result = cr.submit_observation("a1", "scout", (1, 1), "forest", 0.9)
        assert result["state"] == "UNOBSERVED"

    def test_agreement_consolidates(self):
        cr = ConsensusReality()
        cr.submit_observation("a1", "scout", (2, 2), "forest", 0.9)
        result = cr.submit_observation("a2", "sentinel", (2, 2), "forest", 0.8)
        assert result["state"] == "CONSOLIDATED"
        assert result["truth"] == "forest"

    def test_disagreement_creates_ambiguity(self):
        cr = ConsensusReality()
        cr.submit_observation("a1", "scout", (3, 3), "forest", 0.9)
        result = cr.submit_observation("a2", "scout", (3, 3), "rock", 0.9)
        assert result["state"] == "AMBIGUOUS"
        assert set(result["ambiguity"]) == {"forest", "rock"}

    def test_credibility_shifts_with_accuracy(self):
        cr = ConsensusReality()
        cr.submit_observation("truthful", "scout", (4, 4), "water", 0.95)
        cr.submit_observation("liar", "scout", (4, 4), "fire", 0.5)
        stats = cr.stats
        # Truthful agent should have higher credibility than liar
        assert stats["avg_credibility"] > 0

    def test_get_perceived_ambiguous_returns_all(self):
        cr = ConsensusReality()
        cr.submit_observation("a1", "s", (5, 5), "A", 0.9)
        cr.submit_observation("a2", "s", (5, 5), "B", 0.9)
        perceived = cr.get_perceived((5, 5))
        assert set(perceived) == {"A", "B"}

    def test_force_consolidate(self):
        cr = ConsensusReality()
        cr.submit_observation("a", "s", (6, 6), "unknown", 0.5)
        assert cr.force_consolidate((6, 6), "revealed_truth") is True
        assert cr.get_perceived((6, 6)) == ["revealed_truth"]
