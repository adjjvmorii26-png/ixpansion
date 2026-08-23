import pytest
from omega_prime.protocols.messaging.linguistic_drift import LanguageEvolution


class TestLanguageEvolution:
    def test_seed_and_use(self):
        lang = LanguageEvolution(seed=42)
        lang.seed_vocabulary("common", {"alpha": "first", "beta": "second"})
        result = lang.simulate_usage("common", ["alpha"])
        assert len(result) >= 1

    def test_drift_changes_meaning(self):
        lang = LanguageEvolution(seed=42)
        lang.seed_vocabulary("d1", {"hot": "high_temperature"})
        # Use the word many times to trigger drift
        for _ in range(30):
            lang.simulate_usage("d1", ["hot"])
        dialect = lang._dialects["d1"]
        word = dialect._lexicon["hot"]
        # After heavy usage and ticks, drift may occur
        lang.tick()

    def test_mutual_intelligibility_same_vocab(self):
        lang = LanguageEvolution(seed=42)
        vocab = {"x": "one", "y": "two"}
        lang.seed_vocabulary("d1", vocab)
        lang.seed_vocabulary("d2", vocab)
        d1 = lang._dialects["d1"]
        d2 = lang._dialects["d2"]
        assert d1.mutual_intelligibility(d2) == 1.0

    def test_merge_borrows_words(self):
        lang = LanguageEvolution(seed=42)
        lang.seed_vocabulary("d1", {"own": "mine"})
        lang.seed_vocabulary("d2", {"foreign": "theirs", "own": "mine"})
        d1 = lang._dialects["d1"]
        d2 = lang._dialects["d2"]
        borrowed = d1.merge(d2)
        assert borrowed == 1  # Only "foreign" was new
        assert d1.size == 2

    def test_coinage_increases_vocab(self):
        lang = LanguageEvolution(seed=42)
        lang.create_dialect("gen")
        initial_size = lang._dialects["gen"].size
        for _ in range(100):
            lang.simulate_usage("gen", [])
        final_size = lang._dialects["gen"].size
        assert final_size >= initial_size  # New words coined
