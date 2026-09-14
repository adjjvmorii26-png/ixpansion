"""Tests for Wave 641 — Fractal Garden."""
import pytest
from api.wave641_fractal_garden import handler, coherence_vitals, resonates_with

@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    state = Path("data/wave641_fractal_garden.json")
    if state.exists():
        state.unlink()
    yield
    if state.exists():
        state.unlink()

class TestHandler:
    def test_status(self):
        r = handler({})
        assert r["ok"] is True
        assert r["plants"] == 0

    def test_plant(self):
        r = handler({"action": "plant", "module": "wave634_temporal_field", "coherence": 0.8})
        assert r["ok"] is True
        assert r["plant_type"] in ["fern", "blossom", "spiral", "coral", "lattice"]

    def test_grow(self):
        handler({"action": "plant", "module": "m1", "coherence": 0.6})
        r = handler({"action": "grow"})
        assert r["ok"] is True
        assert r["total_plants"] == 1

    def test_grow_season_cycle(self):
        for i in range(30):
            handler({"action": "grow"})
        r = handler({"action": "status"})
        assert r["season"] in ["spring", "summer", "autumn", "winter"]

    def test_render(self):
        handler({"action": "plant", "module": "m1", "coherence": 0.9})
        r = handler({"action": "render"})
        assert r["ok"] is True
        assert "<svg" in r["svg"]
        assert r["artifact"]["plants"] == 1

    def test_render_empty(self):
        r = handler({"action": "render"})
        assert r["ok"] is True
        assert "<svg" in r["svg"]

    def test_gallery(self):
        r = handler({"action": "gallery"})
        assert r["ok"] is True
        assert "artifacts" in r

    def test_plant_types(self):
        handler({"action": "plant", "module": "wave_a"})
        handler({"action": "plant", "module": "wave_b"})
        r = handler({"action": "status"})
        assert r["plants"] == 2

    def test_unknown_action(self):
        r = handler({"action": "nope"})
        assert r["ok"] is False

class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals()
        assert v["wave"] == 641

class TestResonates:
    def test_list(self):
        r = resonates_with()
        assert "wave640_dependency_resolver" in r
        assert "wave98_hex_cathedral" in r
