import pytest
from omega_prime.nucleus.kernel.chronicle_engine import ChronicleEngine, EventWeight


class TestChronicleEngine:
    def test_trivial_events_ignored(self):
        engine = ChronicleEngine()
        entry = engine.observe(1, {"actor": "a", "intent": "idle"})
        assert entry is None

    def test_noteworthy_recorded(self):
        engine = ChronicleEngine()
        entry = engine.observe(1, {"actor": "scout", "intent": "move", "target": "north"})
        assert entry is not None
        assert "scout" in entry.narrative

    def test_legendary_has_dramatic_narrative(self):
        engine = ChronicleEngine()
        entry = engine.observe(1, {"actor": "architect", "intent": "create_realm", "realm": "void"})
        assert "trembled" in entry.narrative

    def test_recall_by_tag(self):
        engine = ChronicleEngine()
        engine.observe(1, {"actor": "s", "intent": "move", "target": "n", "realm": "lattice"})
        results = engine.recall(tags={"lattice"})
        assert len(results) >= 1

    def test_inherit_returns_stories(self):
        engine = ChronicleEngine()
        engine.observe(1, {"actor": "old_one", "intent": "attack", "realm": "continuum"})
        stories = engine.inherit("new_agent")
        assert isinstance(stories, list)

    def test_reputation_accumulates(self):
        engine = ChronicleEngine()
        for _ in range(5):
            engine.observe(1, {"actor": "hero", "intent": "construct", "realm": "lattice"})
        rep = engine.reputation
        assert rep.get("hero", 0) > 0

    def test_stats(self):
        engine = ChronicleEngine()
        engine.observe(1, {"actor": "x", "intent": "move"})
        stats = engine.stats
        assert stats["total_entries"] >= 1
