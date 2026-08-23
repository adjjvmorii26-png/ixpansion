import pytest
from omega_prime.sandbox.fossil_layer import FossilLayer


class TestFossilLayer:
    def test_embed_and_scan(self):
        layer = FossilLayer()
        fid = layer.embed("agent-01", "scout", (5, 5), {"memory": "found_gold"}, tick=10)
        fossils = layer.scan_area(5, 5)
        assert len(fossils) == 1
        assert fossils[0].fossil_id == fid

    def test_excavate_returns_knowledge(self):
        layer = FossilLayer()
        layer.embed("agent-02", "analyst", (3, 3), {"pattern": "swarm", "confidence": 0.9}, tick=5)
        results = layer.excavate_at(3, 3)
        assert len(results) == 1
        assert results[0]["knowledge"]["pattern"] == "swarm"

    def test_eroded_fossils_unrecoverable(self):
        layer = FossilLayer()
        layer.embed("old", "sentinel", (1, 1), {"secret": "data"}, tick=1)
        fossil = layer.scan_area(1, 1)[0]
        fossil.decay_level = 1.0
        assert fossil.is_eroded
        assert fossil.excavate() is None

    def test_partial_erosion_loses_data(self):
        layer = FossilLayer()
        state = {f"key_{i}": f"val_{i}" for i in range(10)}
        layer.embed("mid", "wanderer", (2, 2), state, tick=3)
        fossil = layer.scan_area(2, 2)[0]
        fossil.decay_level = 0.5
        result = fossil.excavate()
        assert result is not None
        assert len(result) < 10  # Some keys lost to erosion

    def test_tick_progresses_decay(self):
        layer = FossilLayer()
        layer.embed("t", "scout", (7, 7), {"d": 1}, tick=1)
        before = layer.stats["pristine"]
        for _ in range(100):
            layer.tick(erosion_rate=0.05)
        after = layer.stats["pristine"]
        assert after <= before

    def test_stats_structure(self):
        layer = FossilLayer()
        layer.embed("s", "sentinel", (0, 0), {}, tick=1)
        stats = layer.stats
        assert "total_fossils" in stats and "by_species" in stats
