"""Tests for Wave 732 — Live Blog Engine."""
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _import_wave(module_name):
    import importlib
    return importlib.import_module(f"api.{module_name}")

class TestWave732LiveBlog:
    def test_module_import(self):
        m = _import_wave("wave732_live_blog")
        assert m.NAME == "live_blog"
        assert m.WAVE == 732

    def test_post_and_latest(self):
        m = _import_wave("wave732_live_blog")
        r = m.handler({"action": "post", "type": "wave_announcement", "title": "Test Wave", "content": "Wave 732 deployed", "tags": ["test", "wave"]})
        assert r["post"]["type"] == "wave_announcement"
        assert r["post"]["title"] == "Test Wave"
        
        r2 = m.handler({"action": "latest", "limit": 5})
        assert r2["total"] >= 1

    def test_filter_by_type(self):
        m = _import_wave("wave732_live_blog")
        r = m.handler({"action": "by_type", "type": "wave_announcement"})
        assert all(p["type"] == "wave_announcement" for p in r["posts"])

    def test_filter_by_tag(self):
        m = _import_wave("wave732_live_blog")
        r = m.handler({"action": "by_tag", "tag": "test"})
        assert len(r["posts"]) >= 1

    def test_search(self):
        m = _import_wave("wave732_live_blog")
        r = m.handler({"action": "search", "query": "Test"})
        assert len(r["posts"]) >= 1

    def test_coherence_vitals(self):
        m = _import_wave("wave732_live_blog")
        v = m.coherence_vitals()
        assert v["wave"] == 732
        assert v["status"] == "active"

    def test_resonates_with(self):
        m = _import_wave("wave732_live_blog")
        r = m.resonates_with()
        assert isinstance(r, list)
        assert 720 in r

if __name__ == "__main__":
    pytest.main([__file__, "-q"])
