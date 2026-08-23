import pytest
from omega_prime.protocols.messaging.semantic_fossilization import SemanticStrata


class TestSemanticFossilization:
    def test_active_word_does_not_fossilize(self):
        strata = SemanticStrata()
        strata.use_word("fresh", "recent")
        fossils = strata.tick()
        assert len(fossils) == 0

    def test_disused_word_fossilizes(self):
        strata = SemanticStrata()
        strata.use_word("ancient_word", "old_meaning")
        # Fast forward past threshold
        strata._tick += SemanticStrata.FOSSILIZATION_THRESHOLD + 1
        fossils = strata.tick()
        assert len(fossils) == 1
        assert fossils[0].token == "ancient_word"
        assert "ancient_word" not in strata._active_words

    def test_excavate_recovers_meaning(self):
        strata = SemanticStrata()
        strata.use_word("buried", "deep_concept")
        strata._tick += SemanticStrata.FOSSILIZATION_THRESHOLD + 1
        strata.tick()
        results = strata.excavate(depth=1)
        assert len(results) == 1
        assert results[0]["word"] == "buried"

    def test_revive_restores_word(self):
        strata = SemanticStrata()
        strata.use_word("dead_lang", "forgotten_tongue")
        strata._tick += SemanticStrata.FOSSILIZATION_THRESHOLD + 1
        strata.tick()
        assert strata.revive_word("dead_lang") is True
        assert "dead_lang" in strata._active_words

    def test_stats(self):
        strata = SemanticStrata()
        strata.use_word("active", "in_use")
        stats = strata.stats
        assert stats["active_vocabulary"] == 1
        assert stats["fossilized_words"] == 0
