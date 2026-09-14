"""Tests for Dream Synthesis Engine (Wave 626)."""
import pytest
from api.wave626_dream_synthesis import (
    DreamSynthesis, DreamPrototype, handler, coherence_vitals,
)


class TestDreamPrototype:
    def test_initial(self):
        d = DreamPrototype("test_dream", "A test dream", ["wave1", "wave2"])
        assert d.name == "test_dream"
        assert 0.5 <= d.novelty_score <= 1.0

    def test_total_score(self):
        d = DreamPrototype("test", "desc", [])
        assert 0.0 <= d.total_score <= 1.0

    def test_to_dict(self):
        d = DreamPrototype("test", "desc", [])
        dd = d.to_dict()
        assert dd["name"] == "test"
        assert "total_score" in dd


class TestDreamSynthesis:
    def test_dream(self):
        engine = DreamSynthesis()
        dream = engine.dream()
        assert "_" in dream.name
        assert len(dream.description) > 10

    def test_dream_batch(self):
        engine = DreamSynthesis()
        dreams = engine.dream_batch(3)
        assert len(dreams) == 3

    def test_realize(self):
        engine = DreamSynthesis()
        engine.dream()
        result = engine.realize(0)
        assert result["ok"] is True
        assert result.get("ok") is True and "skeleton" in result

    def test_realize_out_of_range(self):
        engine = DreamSynthesis()
        result = engine.realize(999)
        assert result["ok"] is False

    def test_top_dreams(self):
        engine = DreamSynthesis()
        engine.dream_batch(5)
        top = engine.get_top_dreams(3)
        assert len(top) == 3
        assert top[0]["total_score"] >= top[-1]["total_score"]

    def test_statistics(self):
        engine = DreamSynthesis()
        engine.dream_batch(3)
        stats = engine.get_statistics()
        assert stats["dream_count"] == 3
        assert stats["total_journal"] == 3


class TestHandler:
    def test_status(self):
        out = handler({"action": "status"})
        assert out["action"] == "status"
        assert out["wave"] == 626

    def test_dream(self):
        out = handler({"action": "dream"})
        assert out["action"] == "dream"
        assert "dream" in out

    def test_dream_batch(self):
        out = handler({"action": "dream_batch", "count": 3})
        assert out["action"] == "dream_batch"
        assert len(out["dreams"]) == 3

    def test_realize(self):
        from api.wave626_dream_synthesis import DreamSynthesis
        engine = DreamSynthesis()
        engine.dream()
        engine.dream()
        result = engine.realize(0)
        assert result["ok"] is True
        assert "skeleton" in result
        # Second realize should fail (already realized)
        result2 = engine.realize(0)
        assert result2["ok"] is False

    def test_top(self):
        out = handler({"action": "top"})
        assert out["action"] == "top"

    def test_journal(self):
        out = handler({"action": "journal"})
        assert out["action"] == "journal"

    def test_realized(self):
        out = handler({"action": "realized"})
        assert out["action"] == "realized"

    def test_statistics(self):
        out = handler({"action": "statistics"})
        assert out["action"] == "statistics"

    def test_unknown(self):
        out = handler({"action": "bogus"})
        assert out["ok"] is False


class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals()
        assert v["wave"] == 626
