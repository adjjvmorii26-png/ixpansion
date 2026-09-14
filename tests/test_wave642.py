"""Tests for Wave 642 — Mythic Narrative Layer."""
import pytest
from api.wave642_mythic_narrative import handler, coherence_vitals, resonates_with

@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    state = Path("data/wave642_mythic_narrative.json")
    if state.exists():
        state.unlink()
    yield
    if state.exists():
        state.unlink()

class TestHandler:
    def test_status(self):
        r = handler({})
        assert r["ok"] is True
        assert r["tick"] == 0

    def test_origin(self):
        r = handler({"action": "origin"})
        assert r["ok"] is True
        assert "seed" in r["origin_myth"].lower()

    def test_hero(self):
        r = handler({"action": "hero", "module": "wave634_temporal_field", "wave": 634, "traits": ["chronic", "temporal"]})
        assert r["ok"] is True
        assert len(r["trials"]) == 5

    def test_epoch(self):
        r = handler({"action": "epoch", "name": "The Social Cognition Era", "theme": "partnerships and self-model"})
        assert r["ok"] is True
        assert r["epoch"] == "The Social Cognition Era"

    def test_cosmology(self):
        r = handler({"action": "cosmology"})
        assert r["ok"] is True
        assert "center" in r["cosmology"]
        assert "throne" in r["cosmology"]

    def test_narrate_season(self):
        r = handler({"action": "narrate", "topic": "season"})
        assert r["ok"] is True
        assert r["tick"] == 1

    def test_narrate_growth(self):
        handler({"action": "hero", "module": "test"})
        r = handler({"action": "narrate", "topic": "growth"})
        assert "1 heroes" in r["narrative"]

    def test_narrate_unknown(self):
        r = handler({"action": "narrate", "topic": "pizza"})
        assert r["ok"] is True

    def test_hero_history_grows(self):
        handler({"action": "hero", "module": "a", "wave": 1})
        handler({"action": "hero", "module": "b", "wave": 2})
        r = handler({"action": "status"})
        assert r["heroes"] == 2

    def test_unknown_action(self):
        r = handler({"action": "nope"})
        assert r["ok"] is False

class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals()
        assert v["wave"] == 642

class TestResonates:
    def test_list(self):
        r = resonates_with()
        assert "wave641_fractal_garden" in r
