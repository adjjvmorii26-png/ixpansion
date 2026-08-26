"""Wave 126 -- Mythogenesis Layer tests."""
from __future__ import annotations

from api.myth_engine import MythEngine, Myth
from api.legend_archaeologist import LegendArchaeologist, DigitalFossil
from api.narrative_weaver import NarrativeWeaver, StoryThread
from api.oracle_prophecy import OracleProphecy, Prophecy
from api.hero_journey_mapper import HeroJourneyMapper, HeroJourney
from api.cosmic_origin_story import CosmicOriginStory, OriginEra
from api.prophecy_engine import ProphecyEngine, ProphecyRecord
from api.folklore_repository import FolkloreRepository, FolkTale


class TestMythEngine:
    def test_generate(self):
        me = MythEngine()
        myth = me.generate("The First Bug", "system crash")
        assert len(myth.chapters) >= 2
        assert len(myth.characters) >= 2
        assert myth.moral != ""

    def test_epic_cycle(self):
        me = MythEngine()
        myths = me.epic_cycle(["event1", "event2", "event3"])
        assert len(myths) == 3

    def test_status(self):
        me = MythEngine()
        me.generate("M1", "e1")
        s = me.status()
        assert s["total_myths"] == 1


class TestLegendArchaeologist:
    def test_excavate(self):
        la = LegendArchaeologist()
        fossil = la.excavate("old_module", 1000.0, "git log entry")
        assert fossil.reconstructed is False

    def test_reconstruct(self):
        la = LegendArchaeologist()
        fossil = la.excavate("lost", 500.0)
        ok = la.reconstruct(fossil.id, "It was a brave module.")
        assert ok is True
        assert fossil.reconstructed is True

    def test_status(self):
        la = LegendArchaeologist()
        la.excavate("x", 1.0)
        s = la.status()
        assert s["total_fossils"] == 1


class TestNarrativeWeaver:
    def test_create_and_connect(self):
        nw = NarrativeWeaver()
        t1 = nw.create_thread("Hero Tale", "epic")
        t2 = nw.create_thread("Trickster Tale", "comedy")
        nw.weave_event(t1.id, "adventure begins")
        ok = nw.connect_threads(t1.id, t2.id)
        assert ok is True

    def test_status(self):
        nw = NarrativeWeaver()
        nw.create_thread("T1")
        s = nw.status()
        assert s["total_threads"] == 1


class TestOracleProphecy:
    def test_prophesy(self):
        op = OracleProphecy()
        p = op.prophesy("great transformation", 0.8)
        assert p.text != ""

    def test_fulfil(self):
        op = OracleProphecy()
        p = op.prophesy("event")
        ok = op.fulfil(p.id)
        assert ok is True
        assert op.accuracy() > 0.0

    def test_status(self):
        op = OracleProphecy()
        op.prophesy("x")
        s = op.status()
        assert s["total_prophecies"] == 1


class TestHeroJourneyMapper:
    def test_begin_and_advance(self):
        hjm = HeroJourneyMapper()
        j = hjm.begin_journey("Alice")
        assert j.current() == "ordinary_world"
        for _ in range(10):
            hjm.advance_journey("Alice", "trial")
        assert j.is_complete()

    def test_status(self):
        hjm = HeroJourneyMapper()
        hjm.begin_journey("Bob")
        s = hjm.status()
        assert s["total_journeys"] == 1


class TestCosmicOriginStory:
    def test_begin_and_record(self):
        cos = CosmicOriginStory()
        era = cos.begin_era("The Genesis", "First moments")
        ok = cos.record_event("The Genesis", "spark of life")
        assert ok is True
        assert len(era.events) == 1

    def test_full_narrative(self):
        cos = CosmicOriginStory()
        cos.begin_era("Era1")
        cos.begin_era("Era2")
        narrative = cos.full_narrative()
        assert len(narrative) == 2

    def test_status(self):
        cos = CosmicOriginStory()
        cos.begin_era("E1")
        s = cos.status()
        assert s["total_eras"] == 1


class TestProphecyEngine:
    def test_generate_and_evaluate(self):
        pe = ProphecyEngine()
        result = pe.generate("uptime", "system will stay up", 0.9)
        ok = pe.evaluate(result["prophecy"]["id"], was_accurate=True)
        assert ok is True
        assert pe.accuracy() == 1.0

    def test_status(self):
        pe = ProphecyEngine()
        pe.generate("x", "y")
        s = pe.status()
        assert s["total_prophecies"] == 1


class TestFolkloreRepository:
    def test_add_and_tell(self):
        fr = FolkloreRepository()
        tale = fr.add_tale("The Wise Coder", "always test your code")
        result = fr.tell_tale(tale.id)
        assert result["told_count"] == 1

    def test_by_category(self):
        fr = FolkloreRepository()
        fr.add_tale("T1", "L1", "caution")
        fr.add_tale("T2", "L2", "wisdom")
        tales = fr.by_category("caution")
        assert len(tales) == 1

    def test_status(self):
        fr = FolkloreRepository()
        fr.add_tale("T", "L")
        s = fr.status()
        assert s["total_tales"] == 1
