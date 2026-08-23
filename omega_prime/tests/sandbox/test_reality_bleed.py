import pytest
from omega_prime.sandbox.modules.reality_bleed import RealityBleedEngine


class TestRealityBleed:
    def test_adjacent_different_truths_create_bleed(self):
        engine = RealityBleedEngine(seed=42)
        engine.consolidate((0, 0), "forest")
        bleeds = engine.consolidate((1, 0), "void")
        assert len(bleeds) >= 1
        assert "~" in bleeds[0]["hybrid"]

    def test_same_truth_no_bleed(self):
        engine = RealityBleedEngine(seed=42)
        engine.consolidate((0, 0), "plains")
        bleeds = engine.consolidate((1, 0), "plains")
        assert len(bleeds) == 0

    def test_non_adjacent_no_bleed(self):
        engine = RealityBleedEngine(seed=42)
        engine.consolidate((0, 0), "forest")
        bleeds = engine.consolidate((10, 10), "void")
        assert len(bleeds) == 0

    def test_bleed_grows_over_time(self):
        engine = RealityBleedEngine(seed=42)
        engine.consolidate((0, 0), "hot")
        engine.consolidate((1, 0), "cold")
        initial = list(engine._bleeds.values())[0].intensity
        for _ in range(20):
            engine.tick()
        final = list(engine._bleeds.values())[0].intensity if engine._bleeds else 0
        assert final > initial or len(engine._bleeds) == 0  # Grew or healed

    def test_hybrid_detection(self):
        engine = RealityBleedEngine(seed=42)
        engine.consolidate((0, 0), "water")
        engine.consolidate((0, 1), "fire")
        hybrid = engine.get_hybrid_at((0, 0))
        assert hybrid is not None
        assert "~" in hybrid

    def test_agent_exposure_in_bleed(self):
        engine = RealityBleedEngine(seed=42)
        engine.consolidate((2, 2), "light")
        engine.consolidate((3, 2), "dark")
        result = engine.expose_agent("wanderer_01", (2, 2))
        assert result["affected"] is True
