import pytest
from omega_prime.agents.cognition.dream_cycle import DreamCycle


class TestDreamCycle:
    def test_not_dreaming_returns_empty(self):
        dream = DreamCycle()
        result = dream.consolidate({"a": "forest", "b": "forest"})
        assert result == []

    def test_consolidate_finds_patterns(self):
        dream = DreamCycle()
        dream.enter_dream()
        fragments = dream.consolidate({
            "cell_1": "forest",
            "cell_2": "forest",
            "cell_3": "rock",
        }, min_support=2)
        assert len(fragments) >= 1
        assert any(f.symbol == "forest" for f in fragments)

    def test_insights_sorted_by_confidence(self):
        dream = DreamCycle()
        dream.enter_dream()
        dream.consolidate({"a": "x", "b": "x", "c": "y"}, min_support=1)
        insights = dream.insights
        if len(insights) > 1:
            assert insights[0]["conf"] >= insights[-1]["conf"]

    def test_depth_increments(self):
        dream = DreamCycle()
        dream.enter_dream()
        dream.exit_dream()
        dream.enter_dream()
        assert dream.depth == 2
